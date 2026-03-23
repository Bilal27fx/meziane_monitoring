"""
plugins/__init__.py - PluginRegistry

Description:
Registre central des plugins business.
Charge et monte dynamiquement les modules sur l'app FastAPI.

Utilisé par:
- main.py (PluginRegistry.load_all + PluginRegistry.register)
- api/dashboard_routes.py (PluginRegistry.get_all_kpis)
"""

from typing import Dict
from fastapi import FastAPI
from sqlalchemy.orm import Session
from app.plugins.base import BusinessModule


class PluginRegistry:
    _plugins: Dict[str, BusinessModule] = {}

    @classmethod
    def register(cls, plugin: BusinessModule) -> None:
        """Enregistre un plugin par son nom"""
        cls._plugins[plugin.name] = plugin

    @classmethod
    def load_all(cls, app: FastAPI) -> None:
        """Monte les routes de tous les plugins + appelle on_startup"""
        for plugin in cls._plugins.values():
            plugin.register_routes(app)
            plugin.on_startup()

    @classmethod
    def get_all_kpis(cls, db: Session) -> dict:
        """Agrège les KPI de tous les plugins pour le dashboard global"""
        return {name: plugin.get_dashboard_kpi(db) for name, plugin in cls._plugins.items()}

    @classmethod
    def get_plugin(cls, name: str) -> BusinessModule:
        return cls._plugins.get(name)
