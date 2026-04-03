import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.utils.db import Base

# Import des modèles pour enregistrer toutes les tables sur Base.metadata.
from app.models import (  # noqa: F401
    sci,
    bien,
    transaction,
    locataire,
    bail,
    quittance,
    locataire_paiement,
    document,
    document_folder,
    document_extraction,
    opportunite,
    simulation,
    user,
    auction_source,
    auction_session,
    auction_listing,
    agent_definition,
    agent_parameter_set,
    agent_run,
    agent_run_event,
)


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
