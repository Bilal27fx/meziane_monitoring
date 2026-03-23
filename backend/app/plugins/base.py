"""
base.py - Classe abstraite BusinessModule

Description:
Interface que chaque plugin business doit implémenter.
Permet l'ajout de nouveaux modules (immobilier, commercial, etc.)
sans modifier le code core.

Utilisé par:
- plugins/immobilier/__init__.py
- plugins/__init__.py (PluginRegistry)
- main.py
"""

from abc import ABC, abstractmethod
from fastapi import FastAPI
from sqlalchemy.orm import Session


class BusinessModule(ABC):
    """Interface à implémenter par chaque plugin business"""

    name: str          # identifiant unique ex: "immobilier"
    version: str       # ex: "1.0.0"
    api_prefix: str    # ex: "/api/immobilier"

    @abstractmethod
    def register_routes(self, app: FastAPI) -> None:
        """Monte les routes APIRouter sur l'application FastAPI"""

    @abstractmethod
    def get_dashboard_kpi(self, db: Session) -> dict:
        """Retourne les KPI principaux pour le dashboard global"""

    def on_startup(self) -> None:
        """Hook optionnel exécuté au démarrage du serveur"""
