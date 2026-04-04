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
from sqlalchemy import text
from app.config import settings
from app.utils.logger import setup_logger
from app.api import sci_routes, bien_routes, transaction_routes, banking_routes, cashflow_routes, locataire_routes, locataire_paiement_routes, document_routes, dashboard_routes, quittance_routes
from app.api import auth_routes, user_routes

from app.models import load_all_models

# Système plugin multi-business
from app.plugins import PluginRegistry
from app.plugins.immobilier import ImmobilierPlugin
from app.tasks.celery_app import celery_app

logger = setup_logger(__name__)

load_all_models()

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
    expose_headers=["Content-Disposition"],
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
app.include_router(user_routes.router)      # Routes Users (admin only)
app.include_router(dashboard_routes.router)  # Routes Dashboard
app.include_router(sci_routes.router)        # Routes SCI
app.include_router(bien_routes.router)       # Routes Biens
app.include_router(transaction_routes.router)  # Routes Transactions
app.include_router(banking_routes.router)    # Routes Banking
app.include_router(cashflow_routes.router)   # Routes Cashflow
app.include_router(locataire_routes.router)  # Routes Locataires
app.include_router(locataire_paiement_routes.router)  # Routes Paiements locataires
app.include_router(document_routes.router)   # Routes Documents
app.include_router(quittance_routes.router)  # Routes Quittances


@app.get("/")
def read_root():  # Health check endpoint
    return {
        "status": "ok",
        "service": "Meziane Monitoring API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
def health_check():  # RFC-007: health check réel — teste DB, retourne 503 si down
    from app.utils.db import SessionLocal
    db_status = "connected"
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception:
        db_status = "error"

    status_code = 200 if db_status == "connected" else 503
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=status_code,
        content={"status": "healthy" if db_status == "connected" else "degraded", "database": db_status}
    )


@app.get("/health/services")
def services_health():  # Retourne état API, base et worker Celery pour header frontend
    from app.utils.db import SessionLocal

    database = "offline"
    celery = "offline"

    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        database = "online"
    except Exception:
        database = "offline"

    try:
        inspector = celery_app.control.inspect(timeout=1.0)
        ping_result = inspector.ping() if inspector else None
        celery = "online" if ping_result else "offline"
    except Exception:
        celery = "offline"

    return {
        "api": "online",
        "database": database,
        "celery": celery,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.DEBUG)
