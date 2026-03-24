"""
categorization_service.py - Service catégorisation IA transactions

Description:
Utilise GPT-4 (OpenAI) pour catégoriser automatiquement les transactions bancaires.
Few-shot learning avec exemples prédéfinis pour accuracy.

Dépendances:
- OpenAI API (GPT-4)
- models.transaction
- config.settings (OPENAI_API_KEY)

Utilisé par:
- api.transaction_routes
- connectors.banking_connector
"""

from typing import Dict
from openai import OpenAI
from app.models.transaction import TransactionCategorie
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class CategorizationService:  # Service catégorisation automatique transactions via GPT-4

    def __init__(self):  # Initialise client OpenAI
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    def categorize_transaction(self, libelle: str, montant: float) -> Dict[str, any]:  # Catégorise transaction via GPT-4
        if not self.client:
            logger.warning("OpenAI API key manquante, catégorisation désactivée")
            return {
                "categorie": TransactionCategorie.AUTRE,
                "confidence": 0.0,
                "raison": "API key OpenAI manquante"
            }

        prompt = f"""Tu es un expert comptable spécialisé en immobilier et SCI (Société Civile Immobilière).

Analyse cette transaction bancaire et catégorise-la parmi les catégories suivantes :

**Catégories possibles :**
- loyer : Paiement de loyer reçu d'un locataire
- charges_copro : Charges de copropriété
- taxe_fonciere : Taxe foncière annuelle
- travaux : Dépenses de travaux, rénovation, maintenance
- remboursement_credit : Remboursement mensuel de crédit immobilier
- assurance : Assurance habitation, PNO, emprunteur
- honoraires : Honoraires agence, notaire, expert-comptable
- frais_bancaires : Frais bancaires, commissions
- autre : Autre type de transaction

**Transaction à analyser :**
- Libellé : "{libelle}"
- Montant : {montant}€ {"(crédit)" if montant > 0 else "(débit)"}

**Exemples de catégorisation :**
- "Virement loyer appartement" → loyer (confiance: 0.95)
- "Charges T1 2026" → charges_copro (confiance: 0.90)
- "Taxe foncière" → taxe_fonciere (confiance: 0.98)
- "Peinture salon" → travaux (confiance: 0.85)
- "Remb pret HSBC" → remboursement_credit (confiance: 0.92)
- "Assurance MMA" → assurance (confiance: 0.88)
- "Honoraires notaire" → honoraires (confiance: 0.95)
- "Frais tenue compte" → frais_bancaires (confiance: 0.90)

**Format de réponse attendu (JSON strict) :**
{{
    "categorie": "<nom_categorie>",
    "confidence": <0.0-1.0>,
    "raison": "<explication courte>"
}}

Réponds UNIQUEMENT avec le JSON, aucun texte supplémentaire."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # RFC-008: 100x moins cher, aussi précis pour la classification
                messages=[
                    {"role": "system", "content": "Tu es un expert comptable immobilier. Tu réponds uniquement en JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )

            # Parse réponse
            import json
            response_text = response.choices[0].message.content.strip()

            # Extraction du JSON (au cas où GPT ajoute du texte)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            result = json.loads(response_text)

            # Validation et conversion
            categorie_str = result["categorie"].lower()
            categorie = TransactionCategorie(categorie_str)

            return {
                "categorie": categorie,
                "confidence": float(result["confidence"]),
                "raison": result["raison"]
            }

        except Exception as e:
            logger.error(f"Erreur catégorisation IA: {e}")
            return {
                "categorie": TransactionCategorie.AUTRE,
                "confidence": 0.0,
                "raison": f"Erreur: {str(e)}"
            }

    def categorize_batch(self, transactions: list) -> list:  # Catégorise plusieurs transactions en batch
        results = []
        for transaction in transactions:
            result = self.categorize_transaction(transaction["libelle"], transaction["montant"])
            results.append({
                "transaction_id": transaction.get("id"),
                **result
            })
        return results
