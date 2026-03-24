"""
banking_tasks.py - Tasks Celery synchronisation bancaire

Description:
Task asynchrone pour synchronisation transactions Bridge.
Déclenché par webhook Bridge ou manuellement.

Dépendances:
- celery_app
- connectors.banking_connector
- utils.db

Utilisé par:
- api.banking_routes (déclenchement manuel)
- beat_schedule (futur webhook)
"""

import asyncio
from app.tasks.celery_app import celery_app
from app.utils.db import SessionLocal
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


@celery_app.task(name="app.tasks.banking_tasks.sync_banking_task", bind=True, max_retries=3)
def sync_banking_task(self, sci_id: int, account_id: int, since: str = None, until: str = None):
    """Synchronise les transactions d'un compte Bridge vers la DB"""
    from app.connectors.banking_connector import BankingConnectorService

    logger.info(f"Démarrage sync_banking_task sci_id={sci_id} account_id={account_id}")

    db = SessionLocal()
    try:
        connector = BankingConnectorService()

        # RFC-007: asyncio.run() remplace new_event_loop() manuel — cleanup automatique
        async def _run():
            authenticated = await connector.authenticate()
            if not authenticated:
                raise ValueError("Échec authentification Bridge")
            return await connector.import_transactions_to_db(
                sci_id=sci_id,
                account_id=account_id,
                db_session=db,
                since=since,
                until=until,
            )

        result = asyncio.run(_run())

        logger.info(f"sync_banking_task terminé: {result}")
        return result

    except Exception as exc:
        logger.error(f"sync_banking_task échoué: {exc}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
    finally:
        db.close()
