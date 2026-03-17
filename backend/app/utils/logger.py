"""
logger.py - Configuration logging structuré

Description:
Setup logging JSON structuré pour toute l'application.
Format uniforme pour faciliter parsing et monitoring.

Dépendances:
- logging standard library
- config.settings

Utilisé par:
- Tous les modules nécessitant logs
"""

import logging
import sys
from app.config import settings

def setup_logger(name: str) -> logging.Logger:  # Crée logger avec format JSON si prod, texte si dev
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
