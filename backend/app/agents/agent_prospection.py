"""
agent_prospection.py - Agent prospection immobilière automatique

Description:
Agent IA autonome qui scrape SeLoger, PAP, LeBonCoin quotidiennement.
Analyse annonces avec GPT-4, score opportunités, notifie Telegram.

Dépendances:
- playwright (scraping)
- openai (scoring IA)
- Telegram Bot API
- models.opportunite

Utilisé par:
- tasks.agent_jobs (job quotidien)
- api.agent_routes (lancement manuel)
"""

import asyncio
import json
import os
import re
from typing import List, Dict, Optional
from datetime import datetime
import httpx
from playwright.async_api import async_playwright, Page
from openai import OpenAI
from sqlalchemy.orm import Session

from app.models.opportunite import Opportunite, SourceAnnonce, StatutOpportunite
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class AgentProspection:  # Agent IA prospection immobilière

    def __init__(self, db: Session):  # Initialise agent avec session DB
        self.db = db
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

        # Critères de recherche
        self.criteres = {
            "prix_max": 300000,
            "surface_min": 30,
            "villes": ["Paris", "Saint-Ouen", "Montreuil", "Pantin", "Bagnolet", "Aubervilliers"],
            "rentabilite_min": 4.5,
            "score_min_notification": 80
        }

    async def scrape_seloger(self) -> List[Dict]:  # Scrape annonces SeLoger
        logger.info("Démarrage scraping SeLoger...")
        annonces = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                # URL SeLoger Paris + proche banlieue, apparts, prix < 300K
                url = (
                    "https://www.seloger.com/list.htm?types=1&projects=2&"
                    "places=[{cp:75},{cp:93}]&price=NaN/300000&sort=d_dt_crea"
                )

                await page.goto(url, timeout=30000)
                await page.wait_for_selector('.cardList', timeout=10000)

                # Récupère cards annonces
                cards = await page.query_selector_all('.CardList__card')
                logger.info(f"Trouvé {len(cards)} annonces SeLoger")

                for card in cards[:20]:  # Limite 20 pour test
                    try:
                        annonce = await self._parse_seloger_card(card)
                        if annonce:
                            annonces.append(annonce)
                    except Exception as e:
                        logger.error(f"Erreur parse card SeLoger: {e}")

            except Exception as e:
                logger.error(f"Erreur scraping SeLoger: {e}")
            finally:
                await browser.close()

        return annonces

    async def _parse_seloger_card(self, card) -> Optional[Dict]:  # Parse card annonce SeLoger
        try:
            titre = await card.text_content('.Summarystyled__Title')
            prix_text = await card.text_content('.Summarystyled__Price')
            surface_text = await card.text_content('.Summarystyled__Surface')
            ville_text = await card.text_content('.Summarystyled__City')
            lien = await card.get_attribute('href')

            # Parse prix
            prix = float(re.sub(r'[^\d]', '', prix_text)) if prix_text else None

            # Parse surface
            surface_match = re.search(r'(\d+)', surface_text) if surface_text else None
            surface = float(surface_match.group(1)) if surface_match else None

            if not prix or not lien:
                return None

            return {
                "source": SourceAnnonce.SELOGER,
                "titre": titre.strip() if titre else "",
                "prix": prix,
                "surface": surface,
                "prix_m2": round(prix / surface, 2) if surface else None,
                "ville": ville_text.strip() if ville_text else "",
                "url_annonce": f"https://www.seloger.com{lien}",
                "description": titre
            }

        except Exception as e:
            logger.error(f"Erreur parse card: {e}")
            return None

    async def scrape_pap(self) -> List[Dict]:  # Scrape annonces PAP
        logger.info("Démarrage scraping PAP...")
        # Implémentation similaire à SeLoger
        # Simplifié pour l'instant
        return []

    async def scrape_leboncoin(self) -> List[Dict]:  # Scrape annonces LeBonCoin
        logger.info("Démarrage scraping LeBonCoin...")
        # Implémentation similaire à SeLoger
        # Simplifié pour l'instant
        return []

    def analyser_avec_ia(self, annonce: Dict) -> Dict:  # Score annonce avec GPT-4
        if not self.openai_client:
            logger.warning("OpenAI API key manquante, scoring désactivé")
            return {
                "score_global": 50,
                "rentabilite_brute": 0,
                "loyer_estime": 0,
                "travaux_estimes": 0,
                "raison_score": "API OpenAI manquante",
                "risques": []
            }

        prompt = f"""Analyse cette annonce immobilière et donne un scoring détaillé.

**Annonce:**
- Titre: {annonce.get('titre', 'N/A')}
- Prix: {annonce.get('prix', 0)}€
- Surface: {annonce.get('surface', 0)}m²
- Prix/m²: {annonce.get('prix_m2', 0)}€
- Ville: {annonce.get('ville', 'N/A')}
- Description: {annonce.get('description', 'N/A')}

**Contexte:**
- Loyers moyens Paris/proche banlieue: 25-35€/m²
- Travaux moyens: 500-1000€/m² si rénovation
- Rentabilité cible: > 4.5% brut

**Ta mission:**
1. Estime le loyer mensuel possible
2. Estime les travaux nécessaires
3. Calcule la rentabilité brute
4. Donne un score global 0-100
5. Liste les risques

Réponds UNIQUEMENT en JSON:
{{
    "loyer_estime": <float>,
    "travaux_estimes": <float>,
    "rentabilite_brute": <float>,
    "score_rentabilite": <int 0-100>,
    "score_emplacement": <int 0-100>,
    "score_etat": <int 0-100>,
    "score_global": <int 0-100>,
    "raison_score": "<explication courte>",
    "risques": ["<risque1>", "<risque2>"]
}}"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Tu es expert en investissement immobilier locatif. Réponds uniquement en JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )

            result_text = response.choices[0].message.content.strip()

            # Nettoie le JSON si besoin
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            result = json.loads(result_text)

            # Calcule rentabilité nette (loyer annuel - charges estimées 20%)
            loyer_annuel = result["loyer_estime"] * 12
            charges_annuelles = loyer_annuel * 0.20
            rentabilite_nette = ((loyer_annuel - charges_annuelles) / annonce["prix"]) * 100 if annonce["prix"] > 0 else 0
            result["rentabilite_nette"] = round(rentabilite_nette, 2)

            return result

        except Exception as e:
            logger.error(f"Erreur analyse IA: {e}")
            return {
                "score_global": 50,
                "rentabilite_brute": 0,
                "rentabilite_nette": 0,
                "loyer_estime": 0,
                "travaux_estimes": 0,
                "raison_score": f"Erreur analyse: {str(e)}",
                "risques": []
            }

    def sauvegarder_opportunite(self, annonce: Dict, scoring: Dict) -> Optional[Opportunite]:  # Sauvegarde opportunité en DB
        try:
            # Vérifie si URL existe déjà
            existing = self.db.query(Opportunite).filter(
                Opportunite.url_annonce == annonce["url_annonce"]
            ).first()

            if existing:
                logger.info(f"Opportunité déjà existante: {annonce['url_annonce']}")
                return existing

            # Crée nouvelle opportunité
            opportunite = Opportunite(
                source=annonce["source"],
                url_annonce=annonce["url_annonce"],
                titre=annonce.get("titre"),
                prix=annonce["prix"],
                surface=annonce.get("surface"),
                prix_m2=annonce.get("prix_m2"),
                ville=annonce.get("ville", ""),
                adresse=annonce.get("adresse"),
                nb_pieces=annonce.get("nb_pieces"),
                description=annonce.get("description"),

                # Scoring IA
                loyer_estime=scoring.get("loyer_estime"),
                travaux_estimes=scoring.get("travaux_estimes"),
                rentabilite_brute=scoring.get("rentabilite_brute"),
                rentabilite_nette=scoring.get("rentabilite_nette"),
                score_rentabilite=scoring.get("score_rentabilite"),
                score_emplacement=scoring.get("score_emplacement"),
                score_etat=scoring.get("score_etat"),
                score_global=scoring.get("score_global"),
                raison_score=scoring.get("raison_score"),
                risques=json.dumps(scoring.get("risques", [])),

                date_detection=datetime.now().date(),
                statut=StatutOpportunite.NOUVEAU
            )

            self.db.add(opportunite)
            self.db.commit()
            self.db.refresh(opportunite)

            logger.info(f"Opportunité sauvegardée: {opportunite.ville} - Score: {opportunite.score_global}")
            return opportunite

        except Exception as e:
            logger.error(f"Erreur sauvegarde opportunité: {e}")
            self.db.rollback()
            return None

    async def run(self) -> Dict:  # Lance scraping complet toutes sources
        logger.info("🤖 Démarrage Agent Prospection...")

        resultats = {
            "total_annonces": 0,
            "total_analysees": 0,
            "total_sauvegardees": 0,
            "notifications_envoyees": 0,
            "erreurs": 0
        }

        # Scrape toutes les sources
        annonces_seloger = await self.scrape_seloger()
        annonces_pap = await self.scrape_pap()
        annonces_leboncoin = await self.scrape_leboncoin()

        toutes_annonces = annonces_seloger + annonces_pap + annonces_leboncoin
        resultats["total_annonces"] = len(toutes_annonces)

        logger.info(f"Total annonces récupérées: {len(toutes_annonces)}")

        # Analyse et sauvegarde
        for annonce in toutes_annonces:
            try:
                # Analyse avec IA
                scoring = self.analyser_avec_ia(annonce)
                resultats["total_analysees"] += 1

                # Sauvegarde si score > 50
                if scoring.get("score_global", 0) >= 50:
                    opportunite = self.sauvegarder_opportunite(annonce, scoring)

                    if opportunite:
                        resultats["total_sauvegardees"] += 1

                        # Notifie si score élevé
                        if scoring.get("score_global", 0) >= self.criteres["score_min_notification"]:
                            self.notifier_telegram(opportunite)
                            resultats["notifications_envoyees"] += 1

            except Exception as e:
                logger.error(f"Erreur traitement annonce: {e}")
                resultats["erreurs"] += 1

        logger.info(f"✅ Agent terminé: {resultats}")
        return resultats

    def _build_notification_message(self, opportunite: Opportunite) -> str:
        return f"""🚨 Nouvelle opportunité détectée !

📍 {opportunite.ville}
💰 Prix: {opportunite.prix:,.0f}€
📐 Surface: {opportunite.surface}m²
💵 Prix/m²: {opportunite.prix_m2:,.0f}€

📊 Score: {opportunite.score_global}/100
📈 Rentabilité: {opportunite.rentabilite_brute}% brut
💸 Loyer estimé: {opportunite.loyer_estime}€/mois

{opportunite.raison_score}

🔗 {opportunite.url_annonce}
"""

    def notifier_telegram(self, opportunite: Opportunite):
        logger.info(f"📱 Envoi notification Telegram pour opportunité {opportunite.id}")

        message = self._build_notification_message(opportunite)
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if bot_token and chat_id:
            try:
                response = httpx.post(
                    f"https://api.telegram.org/bot{bot_token}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": message,
                        "disable_web_page_preview": False,
                    },
                    timeout=10.0,
                )
                response.raise_for_status()
                logger.info("✅ Telegram envoyé")

            except Exception as e:
                logger.error(f"Erreur envoi Telegram: {e}")
        else:
            logger.warning("Variables Telegram manquantes, notification non envoyée")
            logger.info(f"Message preview:\n{message}")
