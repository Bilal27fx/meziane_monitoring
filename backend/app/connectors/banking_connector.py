"""
banking_connector.py - Connecteur API bancaire Bridge

Description:
Interface avec Bridge API pour récupération automatique transactions bancaires.
Gestion connexion multi-banques, synchronisation, refresh tokens.

Dépendances:
- Bridge API (https://docs.bridgeapi.io)
- config.settings (BRIDGE_CLIENT_ID, BRIDGE_CLIENT_SECRET)
- httpx (async)

Utilisé par:
- api.banking_routes
- tasks (jobs synchronisation)
"""

import httpx
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class BankingConnectorService:  # Service connexion et récupération données bancaires via Bridge (async)

    BASE_URL = "https://api.bridgeapi.io/v2"

    def __init__(self):  # Initialise connecteur Bridge
        self.client_id = settings.BRIDGE_CLIENT_ID
        self.client_secret = settings.BRIDGE_CLIENT_SECRET
        self.access_token = None

    def get_headers(self) -> Dict[str, str]:  # Retourne headers HTTP avec token
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Bridge-Version": "2021-06-01"
        }

    async def authenticate(self) -> bool:  # Authentifie application via client credentials
        if not self.client_id or not self.client_secret:
            logger.error("Bridge credentials manquantes dans .env")
            return False

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:  # RFC-007: timeout explicite
                response = await client.post(
                    f"{self.BASE_URL}/authenticate",
                    json={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret
                    },
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()

            data = response.json()
            self.access_token = data.get("access_token")
            logger.info("Authentification Bridge réussie")
            return True

        except httpx.HTTPError as e:
            logger.error(f"Erreur authentification Bridge: {e}")
            return False

    async def list_banks(self) -> List[Dict]:  # Liste toutes les banques supportées
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/banks",
                    headers=self.get_headers()
                )
                response.raise_for_status()
            return response.json().get("resources", [])

        except httpx.HTTPError as e:
            logger.error(f"Erreur récupération liste banques: {e}")
            return []

    async def get_user_accounts(self, user_uuid: str) -> List[Dict]:  # Récupère comptes bancaires d'un utilisateur Bridge
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/accounts",
                    headers=self.get_headers(),
                    params={"user_uuid": user_uuid}
                )
                response.raise_for_status()
            return response.json().get("resources", [])

        except httpx.HTTPError as e:
            logger.error(f"Erreur récupération comptes utilisateur {user_uuid}: {e}")
            return []

    async def get_account_transactions(
        self,
        account_id: int,
        since: Optional[str] = None,
        until: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:  # Récupère transactions d'un compte bancaire
        if not since:
            since = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        if not until:
            until = datetime.now().strftime("%Y-%m-%d")

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:  # RFC-007: 60s pour les transactions
                response = await client.get(
                    f"{self.BASE_URL}/accounts/{account_id}/transactions",
                    headers=self.get_headers(),
                    params={"since": since, "until": until, "limit": limit}
                )
                response.raise_for_status()
            return response.json().get("resources", [])

        except httpx.HTTPError as e:
            logger.error(f"Erreur récupération transactions compte {account_id}: {e}")
            return []

    async def sync_account(self, account_id: int) -> bool:  # Déclenche synchronisation compte bancaire
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.BASE_URL}/accounts/{account_id}/sync",
                    headers=self.get_headers()
                )
                response.raise_for_status()
            logger.info(f"Synchronisation compte {account_id} déclenchée")
            return True

        except httpx.HTTPError as e:
            logger.error(f"Erreur synchronisation compte {account_id}: {e}")
            return False

    async def create_item(self, bank_id: int, redirect_url: str) -> Dict:  # Crée item Bridge pour connexion banque utilisateur
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.BASE_URL}/items",
                    headers=self.get_headers(),
                    json={"bank_id": bank_id, "redirect_url": redirect_url}
                )
                response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Erreur création item Bridge: {e}")
            return {}

    def parse_transaction(self, raw_transaction: Dict) -> Dict:  # Parse transaction Bridge vers format interne
        return {
            "date": raw_transaction.get("date"),
            "montant": float(raw_transaction.get("amount", 0)),
            "libelle": raw_transaction.get("description", ""),
            "compte_bancaire_id": str(raw_transaction.get("account_id")),
            "bridge_id": raw_transaction.get("id"),
            "bridge_data": raw_transaction
        }

    async def import_transactions_to_db(
        self,
        sci_id: int,
        account_id: int,
        db_session,
        since: Optional[str] = None,
        until: Optional[str] = None
    ) -> Dict[str, int]:  # Importe transactions Bridge vers base de données
        from app.services.transaction_service import TransactionService
        from app.schemas.transaction_schema import TransactionCreate

        transaction_service = TransactionService(db_session)

        raw_transactions = await self.get_account_transactions(
            account_id=account_id,
            since=since,
            until=until
        )

        imported = 0
        duplicates = 0
        errors = 0

        for raw_tx in raw_transactions:
            try:
                parsed = self.parse_transaction(raw_tx)

                transaction_data = TransactionCreate(
                    sci_id=sci_id,
                    date=parsed["date"],
                    montant=parsed["montant"],
                    libelle=parsed["libelle"],
                    compte_bancaire_id=parsed["compte_bancaire_id"]
                )

                duplicates_found = transaction_service.detect_duplicates(transaction_data)
                if duplicates_found:
                    duplicates += 1
                    continue

                transaction_service.create_transaction(transaction_data)
                imported += 1

            except Exception as e:
                logger.error(f"Erreur import transaction {raw_tx.get('id')}: {e}")
                errors += 1

        logger.info(f"Import terminé: {imported} importées, {duplicates} doublons, {errors} erreurs")

        return {
            "imported": imported,
            "duplicates": duplicates,
            "errors": errors,
            "total": len(raw_transactions)
        }
