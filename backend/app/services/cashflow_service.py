"""
cashflow_service.py - Service calculs cashflow

Description:
Calcule revenus, dépenses, cashflow net par bien, par SCI, et global.
Analyse tendances mensuelles, annuelles, rentabilité.

Dépendances:
- models.transaction, models.bien, models.sci
- SQLAlchemy Session

Utilisé par:
- api.cashflow_routes
- reporting_service.py
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_, case
from typing import Dict, List, Optional
from datetime import date, datetime
from decimal import Decimal
from app.models.transaction import Transaction, TransactionCategorie
from app.models.bien import Bien
from app.models.sci import SCI


class CashflowService:  # Service calcul cashflow et analytics financiers

    def __init__(self, db: Session):  # Initialise service avec session DB
        self.db = db

    # === Cashflow par Bien ===

    def get_bien_cashflow(
        self,
        bien_id: int,
        annee: Optional[int] = None,
        mois: Optional[int] = None
    ) -> Dict:  # RFC-008: 1 requête CASE au lieu de 3
        query = self.db.query(
            func.sum(case((Transaction.montant > 0, Transaction.montant), else_=0)).label("revenus"),
            func.sum(case((Transaction.montant < 0, func.abs(Transaction.montant)), else_=0)).label("depenses"),
            func.sum(Transaction.montant).label("total"),
        ).filter(Transaction.bien_id == bien_id)

        if annee:
            query = query.filter(extract('year', Transaction.date) == annee)
        if mois:
            query = query.filter(extract('month', Transaction.date) == mois)

        row = query.one()
        return {
            "bien_id": bien_id,
            "revenus": float(row.revenus or 0),
            "depenses": float(row.depenses or 0),
            "cashflow_net": float(row.total or 0),
            "annee": annee,
            "mois": mois
        }

    def get_bien_cashflow_mensuel(self, bien_id: int, annee: int) -> Dict:  # Cashflow mensuel d'un bien — 1 seule requête GROUP BY
        rows = self.db.query(
            extract('month', Transaction.date).label('mois'),
            func.sum(case((Transaction.montant > 0, Transaction.montant), else_=0)).label('revenus'),
            func.sum(case((Transaction.montant < 0, Transaction.montant), else_=0)).label('depenses'),
        ).filter(
            Transaction.bien_id == bien_id,
            extract('year', Transaction.date) == annee,
        ).group_by('mois').all()

        data = {int(r.mois): {"revenus": float(r.revenus or 0), "depenses": abs(float(r.depenses or 0)), "net": float(r.revenus or 0) + float(r.depenses or 0)} for r in rows}
        return {m: data.get(m, {"revenus": 0, "depenses": 0, "net": 0}) for m in range(1, 13)}

    # === Cashflow par SCI ===

    def get_sci_cashflow(
        self,
        sci_id: int,
        annee: Optional[int] = None,
        mois: Optional[int] = None
    ) -> Dict:  # RFC-008: 1 requête CASE au lieu de 3
        query = self.db.query(
            func.sum(case((Transaction.montant > 0, Transaction.montant), else_=0)).label("revenus"),
            func.sum(case((Transaction.montant < 0, func.abs(Transaction.montant)), else_=0)).label("depenses"),
            func.sum(Transaction.montant).label("total"),
        ).filter(Transaction.sci_id == sci_id)

        if annee:
            query = query.filter(extract('year', Transaction.date) == annee)
        if mois:
            query = query.filter(extract('month', Transaction.date) == mois)

        row = query.one()
        return {
            "sci_id": sci_id,
            "revenus": float(row.revenus or 0),
            "depenses": float(row.depenses or 0),
            "cashflow_net": float(row.total or 0),
            "annee": annee,
            "mois": mois
        }

    def get_sci_cashflow_mensuel(self, sci_id: int, annee: int) -> Dict:  # Cashflow mensuel SCI — 1 seule requête GROUP BY
        rows = self.db.query(
            extract('month', Transaction.date).label('mois'),
            func.sum(case((Transaction.montant > 0, Transaction.montant), else_=0)).label('revenus'),
            func.sum(case((Transaction.montant < 0, Transaction.montant), else_=0)).label('depenses'),
        ).filter(
            Transaction.sci_id == sci_id,
            extract('year', Transaction.date) == annee,
        ).group_by('mois').all()

        data = {int(r.mois): {"revenus": float(r.revenus or 0), "depenses": abs(float(r.depenses or 0)), "net": float(r.revenus or 0) + float(r.depenses or 0)} for r in rows}
        return {m: data.get(m, {"revenus": 0, "depenses": 0, "net": 0}) for m in range(1, 13)}

    # === Cashflow Global ===

    def get_global_cashflow(
        self,
        annee: Optional[int] = None,
        mois: Optional[int] = None
    ) -> Dict:  # RFC-008: 1 requête CASE au lieu de 3
        query = self.db.query(
            func.sum(case((Transaction.montant > 0, Transaction.montant), else_=0)).label("revenus"),
            func.sum(case((Transaction.montant < 0, func.abs(Transaction.montant)), else_=0)).label("depenses"),
            func.sum(Transaction.montant).label("total"),
        )

        if annee:
            query = query.filter(extract('year', Transaction.date) == annee)
        if mois:
            query = query.filter(extract('month', Transaction.date) == mois)

        row = query.one()
        return {
            "revenus": float(row.revenus or 0),
            "depenses": float(row.depenses or 0),
            "cashflow_net": float(row.total or 0),
            "annee": annee,
            "mois": mois
        }

    def get_global_cashflow_mensuel(self, annee: int) -> Dict:  # Cashflow mensuel global — 1 seule requête GROUP BY
        rows = self.db.query(
            extract('month', Transaction.date).label('mois'),
            func.sum(case((Transaction.montant > 0, Transaction.montant), else_=0)).label('revenus'),
            func.sum(case((Transaction.montant < 0, Transaction.montant), else_=0)).label('depenses'),
        ).filter(
            extract('year', Transaction.date) == annee,
        ).group_by('mois').all()

        data = {int(r.mois): {"revenus": float(r.revenus or 0), "depenses": abs(float(r.depenses or 0)), "net": float(r.revenus or 0) + float(r.depenses or 0)} for r in rows}
        return {m: data.get(m, {"revenus": 0, "depenses": 0, "net": 0}) for m in range(1, 13)}

    # === Analytics par Catégorie ===

    def get_depenses_by_categorie(
        self,
        sci_id: Optional[int] = None,
        bien_id: Optional[int] = None,
        annee: Optional[int] = None
    ) -> Dict:  # Ventilation dépenses par catégorie
        query = self.db.query(
            Transaction.categorie,
            func.sum(Transaction.montant).label('total')
        ).filter(Transaction.montant < 0)

        if sci_id:
            query = query.filter(Transaction.sci_id == sci_id)
        if bien_id:
            query = query.filter(Transaction.bien_id == bien_id)
        if annee:
            query = query.filter(extract('year', Transaction.date) == annee)

        query = query.group_by(Transaction.categorie)
        results = query.all()

        return {
            str(cat.value) if cat else "non_categorise": abs(float(total))
            for cat, total in results
        }

    # === Rentabilité ===

    def get_bien_rentabilite(self, bien_id: int, annee: int) -> Dict:  # Calcule rentabilité d'un bien
        bien = self.db.query(Bien).filter(Bien.id == bien_id).first()
        if not bien:
            return {}

        cashflow = self.get_bien_cashflow(bien_id, annee)
        revenus_annuels = cashflow["revenus"]
        depenses_annuelles = cashflow["depenses"]
        cashflow_net = cashflow["cashflow_net"]

        valeur_bien = bien.valeur_actuelle or bien.prix_acquisition or 0

        rentabilite_brute = (revenus_annuels / valeur_bien * 100) if valeur_bien > 0 else 0
        rentabilite_nette = (cashflow_net / valeur_bien * 100) if valeur_bien > 0 else 0

        return {
            "bien_id": bien_id,
            "annee": annee,
            "revenus_annuels": revenus_annuels,
            "depenses_annuelles": depenses_annuelles,
            "cashflow_net": cashflow_net,
            "valeur_bien": float(valeur_bien),
            "rentabilite_brute": round(rentabilite_brute, 2),
            "rentabilite_nette": round(rentabilite_nette, 2)
        }

    # === Dashboard Summary ===

    def get_dashboard_summary(self, annee: int) -> Dict:  # Récapitulatif complet pour dashboard
        global_cf = self.get_global_cashflow(annee)
        mensuel = self.get_global_cashflow_mensuel(annee)

        # Total transactions
        nb_transactions = self.db.query(func.count(Transaction.id)).filter(
            extract('year', Transaction.date) == annee
        ).scalar()

        # Par SCI
        sci_list = self.db.query(SCI).all()
        sci_cashflows = []
        for sci in sci_list:
            cf = self.get_sci_cashflow(sci.id, annee)
            sci_cashflows.append({
                "sci_id": sci.id,
                "nom": sci.nom,
                **cf
            })

        return {
            "annee": annee,
            "global": global_cf,
            "mensuel": mensuel,
            "nb_transactions": nb_transactions,
            "par_sci": sci_cashflows
        }
