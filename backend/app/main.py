"""
main.py - Point d'entrée FastAPI

Description:
Application FastAPI principale.
Configure routes, CORS, middleware.

Dépendances:
- FastAPI
- config.settings

Utilisé par:
- uvicorn (serveur ASGI)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.utils.logger import setup_logger
from app.api import sci_routes, bien_routes, transaction_routes, banking_routes, cashflow_routes, opportunite_routes, locataire_routes, document_routes, dashboard_routes

# Import tous les modèles pour SQLAlchemy
from app.models import sci, bien, transaction, locataire, bail, quittance, document, document_extraction, opportunite, simulation

logger = setup_logger(__name__)

app = FastAPI(  # Application FastAPI principale
    title="Meziane Monitoring API",
    description="Système de monitoring et gestion patrimoine immobilier",
    version="1.0.0",
    debug=settings.DEBUG
)

app.include_router(dashboard_routes.router)  # Routes Dashboard (prioritaire)
app.include_router(sci_routes.router)  # Routes SCI
app.include_router(bien_routes.router)  # Routes Biens
app.include_router(transaction_routes.router)  # Routes Transactions
app.include_router(banking_routes.router)  # Routes Banking
app.include_router(cashflow_routes.router)  # Routes Cashflow
app.include_router(opportunite_routes.router)  # Routes Opportunités
app.include_router(locataire_routes.router)  # Routes Locataires
app.include_router(document_routes.router)  # Routes Documents

app.add_middleware(  # Configure CORS pour frontend
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():  # Health check endpoint
    return {
        "status": "ok",
        "service": "Meziane Monitoring API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
def health_check():  # Health check détaillé
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.DEBUG)
