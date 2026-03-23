"""
dashboard_service.py - Service Dashboard avec calculs KPI

Description:
Service métier pour agréger toutes les données du dashboard Bloomberg.
Calcule KPI, cashflow, patrimoine, alertes, top biens, vue SCI, etc.

Dépendances:
- models (SCI, Bien, Transaction, Locataire, Bail, Quittance, Opportunite)
- services.cashflow_service
- SQLAlchemy Session

Utilisé par:
- api.dashboard_routes
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, extract, and_, or_, desc, case
from typing import Dict, List, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal

from app.models.sci import SCI
from app.models.bien import Bien, StatutBien
from app.models.transaction import Transaction, TransactionCategorie
from app.models.locataire import Locataire
from app.models.bail import Bail, StatutBail
from app.models.quittance import Quittance, StatutQuittance
from app.models.opportunite import Opportunite, StatutOpportunite
from app.services.cashflow_service import CashflowService


class DashboardService:
    """Service centralisant tous les calculs du dashboard"""

    def __init__(self, db: Session):
        self.db = db
        self.cashflow_service = CashflowService(db)

    # === KPI PRINCIPAL ===

    def get_kpi(self) -> Dict:
        """Calcule tous les KPI principaux du dashboard"""

        # 1. Patrimoine Net
        patrimoine_net = self._calculate_patrimoine_net()

        # 2. Cashflow Today (cumul du mois en cours)
        cashflow_today = self._calculate_cashflow_today()

        # 3. Alertes
        nb_alertes = self._count_alertes()

        # 4. Performance YTD (Year To Date)
        performance_ytd = self._calculate_performance_ytd()

        # 5. Taux d'occupation
        taux_occupation = self._calculate_taux_occupation()

        # 6. Nombre de locataires actifs
        nb_locataires_actifs = self._count_locataires_actifs()

        return {
            "patrimoine_net": round(patrimoine_net, 2),
            "cashflow_today": round(cashflow_today, 2),
            "nb_alertes": nb_alertes,
            "performance_ytd": round(performance_ytd, 2),
            "taux_occupation": round(taux_occupation, 2),
            "nb_locataires_actifs": nb_locataires_actifs
        }

    def _calculate_patrimoine_net(self) -> float:
        """Calcule patrimoine net total (somme valeur actuelle de tous les biens)"""
        result = self.db.query(
            func.sum(Bien.valeur_actuelle)
        ).filter(
            Bien.valeur_actuelle.isnot(None)
        ).scalar()

        return float(result or 0)

    def _calculate_cashflow_today(self) -> float:
        """Cashflow cumulé du mois en cours"""
        current_month = datetime.now().month
        current_year = datetime.now().year

        result = self.db.query(
            func.sum(Transaction.montant)
        ).filter(
            extract('year', Transaction.date) == current_year,
            extract('month', Transaction.date) == current_month
        ).scalar()

        return float(result or 0)

    def _count_alertes(self) -> int:
        """Compte les alertes actives (loyers impayés + nouvelles opportunités)"""

        # Loyers impayés
        nb_impayes = self.db.query(func.count(Quittance.id)).filter(
            Quittance.statut.in_([StatutQuittance.IMPAYE, StatutQuittance.PARTIEL])
        ).scalar() or 0

        # Nouvelles opportunités (non vues)
        nb_opportunites = self.db.query(func.count(Opportunite.id)).filter(
            Opportunite.statut == StatutOpportunite.NOUVEAU
        ).scalar() or 0

        return nb_impayes + nb_opportunites

    def _calculate_performance_ytd(self) -> float:
        """Performance année en cours (rentabilité nette moyenne)"""
        current_year = datetime.now().year

        # Cashflow net YTD
        cashflow_ytd = self.cashflow_service.get_global_cashflow(current_year)
        cashflow_net = cashflow_ytd.get("cashflow_net", 0)

        # Patrimoine
        patrimoine = self._calculate_patrimoine_net()

        if patrimoine == 0:
            return 0.0

        # Rentabilité = (cashflow_net / patrimoine) * 100
        return (cashflow_net / patrimoine) * 100

    def _calculate_taux_occupation(self) -> float:
        """Taux d'occupation (% biens loués)"""
        total_biens = self.db.query(func.count(Bien.id)).scalar() or 0

        if total_biens == 0:
            return 0.0

        biens_loues = self.db.query(func.count(Bien.id)).filter(
            Bien.statut == StatutBien.LOUE
        ).scalar() or 0

        return (biens_loues / total_biens) * 100

    def _count_locataires_actifs(self) -> int:
        """Nombre de locataires avec bail actif"""
        return self.db.query(func.count(Bail.locataire_id.distinct())).filter(
            Bail.statut == StatutBail.ACTIF
        ).scalar() or 0

    # === CASHFLOW 30 DERNIERS JOURS ===

    def get_cashflow_30days(self) -> List[Dict]:
        """Retourne données cashflow pour les 30 derniers jours"""
        today = date.today()
        date_debut = today - timedelta(days=30)

        # Récupère toutes les transactions des 30 derniers jours
        transactions = self.db.query(Transaction).filter(
            Transaction.date >= date_debut,
            Transaction.date <= today
        ).order_by(Transaction.date).all()

        # Agrège par jour
        daily_data = {}
        for tx in transactions:
            day_key = tx.date.isoformat()
            if day_key not in daily_data:
                daily_data[day_key] = {
                    "date": day_key,
                    "revenus": 0.0,
                    "depenses": 0.0,
                    "net": 0.0
                }

            if tx.montant > 0:
                daily_data[day_key]["revenus"] += tx.montant
            else:
                daily_data[day_key]["depenses"] += abs(tx.montant)

            daily_data[day_key]["net"] += tx.montant

        # Rempli les jours manquants avec des zéros
        result = []
        current = date_debut
        while current <= today:
            day_key = current.isoformat()
            if day_key in daily_data:
                result.append(daily_data[day_key])
            else:
                result.append({
                    "date": day_key,
                    "revenus": 0.0,
                    "depenses": 0.0,
                    "net": 0.0
                })
            current += timedelta(days=1)

        return result

    # === ÉVOLUTION PATRIMOINE 12 MOIS ===

    def get_patrimoine_12months(self) -> List[Dict]:
        """Évolution patrimoine sur 12 derniers mois — basée sur les transactions cumulées"""
        today = date.today()

        # Valeur actuelle du patrimoine
        patrimoine_actuel = self._calculate_patrimoine_net()

        # Cashflow cumulé par mois depuis 12 mois (GROUP BY)
        rows = self.db.query(
            extract('year', Transaction.date).label('annee'),
            extract('month', Transaction.date).label('mois'),
            func.sum(Transaction.montant).label('total'),
        ).filter(
            Transaction.date >= today - timedelta(days=365)
        ).group_by('annee', 'mois').order_by('annee', 'mois').all()

        cashflow_par_mois = {
            f"{int(r.annee)}-{int(r.mois):02d}": float(r.total or 0)
            for r in rows
        }

        # Reconstitue l'évolution en soustrayant du patrimoine actuel (de la fin vers le début)
        result = []
        valeur_courante = patrimoine_actuel
        mois_list = []

        for i in range(11, -1, -1):
            ref = today - timedelta(days=30 * i)
            mois_list.append(ref.strftime("%Y-%m"))

        for mois_key in reversed(mois_list):
            cf = cashflow_par_mois.get(mois_key, 0)
            result.append({"date": mois_key, "valeur": round(valeur_courante, 2)})
            valeur_courante -= cf  # Recule dans le temps

        result.reverse()
        return result

    # === DERNIÈRES TRANSACTIONS ===

    def get_recent_transactions(self, limit: int = 10) -> List[Dict]:
        """Récupère les N dernières transactions avec détails"""
        transactions = self.db.query(Transaction).join(
            SCI, Transaction.sci_id == SCI.id
        ).outerjoin(
            Bien, Transaction.bien_id == Bien.id
        ).order_by(
            desc(Transaction.date),
            desc(Transaction.created_at)
        ).limit(limit).all()

        result = []
        for tx in transactions:
            result.append({
                "id": tx.id,
                "date": tx.date.isoformat(),
                "montant": float(tx.montant),
                "libelle": tx.libelle,
                "categorie": tx.categorie.value if tx.categorie else None,
                "sci_nom": tx.sci.nom if tx.sci else None,
                "bien_adresse": tx.bien.adresse if tx.bien else None,
                "statut_validation": tx.statut_validation.value
            })

        return result

    # === TOP 5 BIENS PAR RENTABILITÉ ===

    def get_top_biens_by_rentabilite(self, limit: int = 5) -> List[Dict]:
        """Top biens par rentabilité — 2 requêtes au lieu de N×3"""
        current_year = datetime.now().year

        # 1. Cashflow annuel par bien (1 requête GROUP BY)
        cashflow_rows = self.db.query(
            Transaction.bien_id,
            func.sum(case((Transaction.montant > 0, Transaction.montant), else_=0)).label('revenus'),
            func.sum(case((Transaction.montant < 0, Transaction.montant), else_=0)).label('depenses'),
            func.sum(Transaction.montant).label('cashflow_net'),
        ).filter(
            Transaction.bien_id.isnot(None),
            extract('year', Transaction.date) == current_year,
        ).group_by(Transaction.bien_id).all()
        cashflow_map = {r.bien_id: r for r in cashflow_rows}

        # 2. Biens avec valeur (1 requête)
        biens = self.db.query(Bien).filter(Bien.valeur_actuelle.isnot(None)).all()

        result = []
        for bien in biens:
            cf = cashflow_map.get(bien.id)
            revenus = float(cf.revenus or 0) if cf else 0
            cashflow_net = float(cf.cashflow_net or 0) if cf else 0
            valeur = float(bien.valeur_actuelle)
            rentabilite_brute = (revenus / valeur * 100) if valeur > 0 else 0
            rentabilite_nette = (cashflow_net / valeur * 100) if valeur > 0 else 0
            result.append({
                "id": bien.id,
                "adresse": bien.adresse,
                "ville": bien.ville,
                "type_bien": bien.type_bien.value,
                "valeur_actuelle": valeur,
                "rentabilite_brute": round(rentabilite_brute, 2),
                "rentabilite_nette": round(rentabilite_nette, 2),
                "cashflow_annuel": cashflow_net,
            })

        result.sort(key=lambda x: x["rentabilite_nette"], reverse=True)
        return result[:limit]

    # === VUE D'ENSEMBLE SCI ===

    def get_sci_overview(self) -> List[Dict]:
        """Vue d'ensemble SCI — 3 requêtes agrégées au lieu de N×3"""
        current_year = datetime.now().year

        # 1. Toutes les SCI
        sci_list = self.db.query(SCI).all()

        # 2. Stats biens par SCI (1 requête GROUP BY)
        bien_stats = self.db.query(
            Bien.sci_id,
            func.count(Bien.id).label('nb_biens'),
            func.sum(Bien.valeur_actuelle).label('valeur_totale'),
        ).group_by(Bien.sci_id).all()
        bien_map = {r.sci_id: r for r in bien_stats}

        # 3. Cashflow par SCI année en cours (1 requête GROUP BY)
        cf_rows = self.db.query(
            Transaction.sci_id,
            func.sum(case((Transaction.montant > 0, Transaction.montant), else_=0)).label('revenus'),
            func.sum(case((Transaction.montant < 0, Transaction.montant), else_=0)).label('depenses'),
            func.sum(Transaction.montant).label('cashflow_net'),
        ).filter(
            extract('year', Transaction.date) == current_year,
        ).group_by(Transaction.sci_id).all()
        cf_map = {r.sci_id: r for r in cf_rows}

        result = []
        for sci in sci_list:
            bs = bien_map.get(sci.id)
            cf = cf_map.get(sci.id)
            result.append({
                "id": sci.id,
                "nom": sci.nom,
                "siret": sci.siret,
                "nb_biens": int(bs.nb_biens) if bs else 0,
                "valeur_patrimoniale": float(bs.valeur_totale or 0) if bs else 0,
                "cashflow_annuel": float(cf.cashflow_net or 0) if cf else 0,
                "revenus_annuels": float(cf.revenus or 0) if cf else 0,
                "depenses_annuelles": abs(float(cf.depenses or 0)) if cf else 0,
            })
        return result

    # === LOCATAIRES AVEC STATUT PAIEMENT ===

    def get_locataires_overview(self) -> List[Dict]:
        """Liste locataires avec bail actif — joinedload au lieu de N×3 requêtes"""

        # 1. Baux actifs avec locataire et bien chargés en 1 requête (joinedload)
        baux = self.db.query(Bail).filter(
            Bail.statut == StatutBail.ACTIF
        ).options(
            joinedload(Bail.locataire),
            joinedload(Bail.bien),
        ).all()

        bail_ids = [b.id for b in baux]
        if not bail_ids:
            return []

        # 2. Nb impayés par bail (1 requête GROUP BY)
        impayes_rows = self.db.query(
            Quittance.bail_id,
            func.count(Quittance.id).label('nb'),
        ).filter(
            Quittance.bail_id.in_(bail_ids),
            Quittance.statut.in_([StatutQuittance.IMPAYE, StatutQuittance.PARTIEL]),
        ).group_by(Quittance.bail_id).all()
        impayes_map = {r.bail_id: r.nb for r in impayes_rows}

        # 3. Dernière quittance par bail (1 requête avec rank)
        # On utilise une sous-requête max(annee*100+mois) pour éviter window functions
        derniere_q_sub = self.db.query(
            Quittance.bail_id,
            func.max(Quittance.annee * 100 + Quittance.mois).label('max_period'),
        ).filter(Quittance.bail_id.in_(bail_ids)).group_by(Quittance.bail_id).subquery()

        dernieres_q = self.db.query(Quittance).join(
            derniere_q_sub,
            and_(
                Quittance.bail_id == derniere_q_sub.c.bail_id,
                Quittance.annee * 100 + Quittance.mois == derniere_q_sub.c.max_period,
            )
        ).all()
        derniere_map = {q.bail_id: q for q in dernieres_q}

        result = []
        for bail in baux:
            if not bail.locataire:
                continue
            derniere_q = derniere_map.get(bail.id)
            result.append({
                "id": bail.locataire.id,
                "nom": bail.locataire.nom,
                "prenom": bail.locataire.prenom,
                "email": bail.locataire.email,
                "telephone": bail.locataire.telephone,
                "bien_adresse": bail.bien.adresse if bail.bien else None,
                "loyer_mensuel": float(bail.loyer_mensuel),
                "statut_paiement": derniere_q.statut.value if derniere_q else "en_attente",
                "nb_impayes": impayes_map.get(bail.id, 0),
                "date_debut_bail": bail.date_debut.isoformat(),
            })
        return result

    # === OPPORTUNITÉS IA ===

    def get_opportunites_overview(self, limit: int = 10) -> List[Dict]:
        """Top opportunités détectées par agent IA"""

        opportunites = self.db.query(Opportunite).filter(
            Opportunite.statut.in_([
                StatutOpportunite.NOUVEAU,
                StatutOpportunite.VU
            ])
        ).order_by(
            desc(Opportunite.score_global),
            desc(Opportunite.date_detection)
        ).limit(limit).all()

        result = []

        for opp in opportunites:
            result.append({
                "id": opp.id,
                "titre": opp.titre,
                "ville": opp.ville,
                "prix": float(opp.prix),
                "surface": float(opp.surface) if opp.surface else None,
                "prix_m2": float(opp.prix_m2) if opp.prix_m2 else None,
                "nb_pieces": opp.nb_pieces,
                "score_global": opp.score_global,
                "rentabilite_brute": float(opp.rentabilite_brute) if opp.rentabilite_brute else None,
                "rentabilite_nette": float(opp.rentabilite_nette) if opp.rentabilite_nette else None,
                "source": opp.source.value,
                "url_annonce": opp.url_annonce,
                "date_detection": opp.date_detection.isoformat(),
                "statut": opp.statut.value
            })

        return result

    # === DASHBOARD COMPLET ===

    def get_full_dashboard(self) -> Dict:
        """Retourne toutes les données du dashboard en une seule requête"""

        return {
            "kpi": self.get_kpi(),
            "cashflow_30days": self.get_cashflow_30days(),
            "patrimoine_12months": self.get_patrimoine_12months(),
            "recent_transactions": self.get_recent_transactions(10),
            "top_biens": self.get_top_biens_by_rentabilite(5),
            "sci_overview": self.get_sci_overview(),
            "locataires": self.get_locataires_overview(),
            "opportunites": self.get_opportunites_overview(10)
        }
