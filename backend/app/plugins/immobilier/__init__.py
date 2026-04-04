"""
immobilier/__init__.py - Plugin Immobilier France

Description:
Plugin wrappant tout le code immobilier existant.
Monte les routes SCI, Bien, Locataire, Transaction, Cashflow, etc.
sur le prefix /api/immobilier (compatible avec les routes actuelles /api/*).

Utilisé par:
- main.py via PluginRegistry.register(ImmobilierPlugin())
"""

from fastapi import FastAPI
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.plugins.base import BusinessModule
from app.models.sci import SCI
from app.models.bien import Bien, StatutBien
from app.models.bail import Bail, StatutBail
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ImmobilierPlugin(BusinessModule):
    """Plugin immobilier France — wrapping des modules existants"""

    name = "immobilier"
    version = "1.0.0"
    api_prefix = "/api"  # Conserve les routes actuelles /api/sci, /api/biens, etc.

    def register_routes(self, app: FastAPI) -> None:
        """Les routes sont déjà montées dans main.py — pas de double montage"""
        logger.info("ImmobilierPlugin: routes déjà enregistrées via main.py")

    def get_dashboard_kpi(self, db: Session) -> dict:
        """Retourne les KPI immobilier pour le dashboard global"""
        nb_biens = db.query(func.count(Bien.id)).scalar() or 0
        nb_biens_loues = db.query(func.count(Bien.id)).filter(Bien.statut == StatutBien.LOUE).scalar() or 0
        valeur_totale = db.query(func.sum(Bien.valeur_actuelle)).filter(Bien.valeur_actuelle.isnot(None)).scalar() or 0
        nb_sci = db.query(func.count(SCI.id)).scalar() or 0
        nb_locataires = db.query(func.count(Bail.id)).filter(Bail.statut == StatutBail.ACTIF).scalar() or 0
        return {
            "nb_sci": nb_sci,
            "nb_biens": nb_biens,
            "nb_biens_loues": nb_biens_loues,
            "taux_occupation": round(nb_biens_loues / nb_biens * 100, 1) if nb_biens > 0 else 0,
            "valeur_patrimoniale": float(valeur_totale),
            "nb_locataires_actifs": nb_locataires,
            "nb_opportunites_nouvelles": 0,
        }

    def on_startup(self) -> None:
        logger.info(f"Plugin '{self.name}' v{self.version} démarré")
