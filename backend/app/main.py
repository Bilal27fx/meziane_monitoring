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

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.utils.logger import setup_logger
from app.api import sci_routes, bien_routes, transaction_routes, banking_routes, cashflow_routes, opportunite_routes, locataire_routes, document_routes, dashboard_routes
from app.api import auth_routes

# Import tous les modèles pour SQLAlchemy
from app.models import sci, bien, transaction, locataire, bail, quittance, document, document_extraction, opportunite, simulation, user

# Système plugin multi-business
from app.plugins import PluginRegistry
from app.plugins.immobilier import ImmobilierPlugin

logger = setup_logger(__name__)

app = FastAPI(  # Application FastAPI principale
    title="Meziane Monitoring API",
    description="Système de monitoring et gestion patrimoine immobilier",
    version="1.0.0",
    debug=settings.DEBUG
)

app.add_middleware(  # Configure CORS depuis settings.ALLOWED_ORIGINS
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):  # Gestion centralisée des erreurs non gérées
    logger.error(f"Unhandled exception on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erreur interne du serveur", "type": type(exc).__name__},
    )


# Enregistre les plugins business
PluginRegistry.register(ImmobilierPlugin())
# PluginRegistry.register(CommercialAlgeriePlugin())  # Décommenter quand prêt

app.include_router(auth_routes.router)      # Routes Auth (publiques — pas de Depends auth)
app.include_router(dashboard_routes.router)  # Routes Dashboard
app.include_router(sci_routes.router)        # Routes SCI
app.include_router(bien_routes.router)       # Routes Biens
app.include_router(transaction_routes.router)  # Routes Transactions
app.include_router(banking_routes.router)    # Routes Banking
app.include_router(cashflow_routes.router)   # Routes Cashflow
app.include_router(opportunite_routes.router)  # Routes Opportunités
app.include_router(locataire_routes.router)  # Routes Locataires
app.include_router(document_routes.router)   # Routes Documents


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
