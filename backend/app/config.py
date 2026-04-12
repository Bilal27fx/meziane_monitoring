"""
config.py - Configuration application

Description:
Charge et valide toutes les variables d'environnement.
Utilise Pydantic Settings pour validation stricte.

Dépendances:
- pydantic-settings
- python-dotenv

Utilisé par:
- Tous les modules nécessitant accès config (DB, API keys, etc.)
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
from pathlib import Path


class Settings(BaseSettings):  # Configuration globale application chargée depuis .env
    # Database
    POSTGRES_USER: str = "meziane"
    POSTGRES_PASSWORD: str = "meziane_dev_2026"
    POSTGRES_DB: str = "meziane_monitoring"
    DATABASE_URL: str = "postgresql://meziane:meziane_dev_2026@localhost:5432/meziane_monitoring"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_BUCKET_DOCUMENTS: str = "documents-sci"
    MINIO_BUCKET_REPORTS: str = "rapports"
    MINIO_BUCKET_EXPORTS: str = "exports"
    MINIO_SECURE: bool = False

    # API Keys
    BRIDGE_API_KEY: Optional[str] = None
    BRIDGE_CLIENT_ID: Optional[str] = None
    BRIDGE_CLIENT_SECRET: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    # Application
    SECRET_KEY: str = "dev_secret_key_change_in_production"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None

    # Twilio (WhatsApp)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_WHATSAPP_FROM: Optional[str] = None
    TWILIO_WHATSAPP_TO: Optional[str] = None

    # LangSmith
    LANGCHAIN_TRACING_V2: str = "false"
    LANGSMITH_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "meziane-licitor-dev"

    class Config:
        env_file = str(Path(__file__).parent.parent / ".env")
        case_sensitive = True
        extra = "ignore"


settings = Settings()  # Instance singleton configuration
