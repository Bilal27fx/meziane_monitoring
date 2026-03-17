"""
simulation.py - Modèle Simulation acquisition

Description:
Représente simulation d'achat immobilier avec calculs financiers.
Paramètres input, résultats calculs, recommandation IA.

Dépendances:
- opportunite.py (clé étrangère optionnelle)
- utils.db.Base

Utilisé par:
- acquisition_service.py
"""

from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, JSON
from app.utils.db import Base
from datetime import datetime
import enum


class StatutSimulation(str, enum.Enum):  # Statut simulation
    SIMULE = "simule"
    EN_COURS = "en_cours"
    REALISE = "realise"
    ABANDONNE = "abandonne"


class Simulation(Base):  # Représente simulation acquisition immobilière
    __tablename__ = "simulations_acquisition"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=True)
    opportunite_id = Column(Integer, ForeignKey("opportunites_immobilieres.id"), nullable=True)

    # Dates
    date_simulation = Column(Date, nullable=False, default=datetime.utcnow)

    # Paramètres (JSON)
    params_json = Column(JSON, nullable=False)

    # Résultats (JSON)
    resultats_json = Column(JSON, nullable=False)

    # IA Recommandation
    recommandation_ia = Column(String(20), nullable=True)
    recommandation_details = Column(JSON, nullable=True)

    # Statut
    statut = Column(Enum(StatutSimulation), nullable=False, default=StatutSimulation.SIMULE)

    def __repr__(self):
        return f"<Simulation {self.date_simulation} - {self.statut.value}>"
