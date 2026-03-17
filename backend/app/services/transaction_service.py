"""
transaction_service.py - Service gestion transactions bancaires

Description:
Logique métier pour gestion des transactions bancaires.
CRUD, filtrage, catégorisation, validation.

Dépendances:
- models.transaction
- schemas.transaction_schema
- SQLAlchemy Session

Utilisé par:
- api.transaction_routes
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, extract, func
from typing import List, Optional
from datetime import date, datetime
from app.models.transaction import Transaction, TransactionCategorie, StatutValidation
from app.schemas.transaction_schema import TransactionCreate, TransactionUpdate


class TransactionService:  # Service gestion transactions bancaires

    def __init__(self, db: Session):  # Initialise service avec session DB
        self.db = db

    # === CRUD Methods ===

    def get_all_transactions(
        self,
        sci_id: Optional[int] = None,
        bien_id: Optional[int] = None,
        categorie: Optional[TransactionCategorie] = None,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
        statut_validation: Optional[StatutValidation] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Transaction]:  # Récupère transactions avec filtres optionnels
        query = self.db.query(Transaction)

        if sci_id:
            query = query.filter(Transaction.sci_id == sci_id)
        if bien_id:
            query = query.filter(Transaction.bien_id == bien_id)
        if categorie:
            query = query.filter(Transaction.categorie == categorie)
        if date_debut:
            query = query.filter(Transaction.date >= date_debut)
        if date_fin:
            query = query.filter(Transaction.date <= date_fin)
        if statut_validation:
            query = query.filter(Transaction.statut_validation == statut_validation)

        return query.order_by(Transaction.date.desc()).limit(limit).offset(offset).all()

    def get_transaction_by_id(self, transaction_id: int) -> Optional[Transaction]:  # Récupère transaction par ID
        return self.db.query(Transaction).filter(Transaction.id == transaction_id).first()

    def create_transaction(self, transaction_data: TransactionCreate) -> Transaction:  # Crée nouvelle transaction
        transaction = Transaction(**transaction_data.model_dump())
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def create_bulk_transactions(self, transactions_data: List[TransactionCreate]) -> List[Transaction]:  # Crée plusieurs transactions en masse
        transactions = [Transaction(**data.model_dump()) for data in transactions_data]
        self.db.add_all(transactions)
        self.db.commit()
        for t in transactions:
            self.db.refresh(t)
        return transactions

    def update_transaction(self, transaction_id: int, transaction_data: TransactionUpdate) -> Optional[Transaction]:  # Met à jour transaction existante
        transaction = self.get_transaction_by_id(transaction_id)
        if not transaction:
            return None

        update_data = transaction_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(transaction, field, value)

        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def delete_transaction(self, transaction_id: int) -> bool:  # Supprime transaction par ID
        transaction = self.get_transaction_by_id(transaction_id)
        if not transaction:
            return False

        self.db.delete(transaction)
        self.db.commit()
        return True

    # === Validation Methods ===

    def valider_transaction(self, transaction_id: int, validateur: str) -> Optional[Transaction]:  # Valide transaction manuellement
        transaction = self.get_transaction_by_id(transaction_id)
        if not transaction:
            return None

        transaction.statut_validation = StatutValidation.VALIDE
        transaction.valide_par = validateur
        transaction.date_validation = date.today()

        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def rejeter_transaction(self, transaction_id: int, validateur: str) -> Optional[Transaction]:  # Rejette transaction
        transaction = self.get_transaction_by_id(transaction_id)
        if not transaction:
            return None

        transaction.statut_validation = StatutValidation.REJETE
        transaction.valide_par = validateur
        transaction.date_validation = date.today()

        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    # === Analytics Methods ===

    def get_total_by_categorie(self, sci_id: Optional[int] = None, annee: Optional[int] = None) -> dict:  # Calcule total par catégorie
        query = self.db.query(
            Transaction.categorie,
            func.sum(Transaction.montant).label("total")
        )

        if sci_id:
            query = query.filter(Transaction.sci_id == sci_id)
        if annee:
            query = query.filter(extract('year', Transaction.date) == annee)

        query = query.group_by(Transaction.categorie)
        results = query.all()

        return {
            str(cat.value) if cat else "non_categorise": float(total)
            for cat, total in results
        }

    def get_total_mensuel(self, sci_id: int, annee: int) -> dict:  # Calcule total mensuel pour une SCI
        query = self.db.query(
            extract('month', Transaction.date).label('mois'),
            func.sum(Transaction.montant).label('total')
        ).filter(
            Transaction.sci_id == sci_id,
            extract('year', Transaction.date) == annee
        ).group_by('mois').order_by('mois')

        results = query.all()

        return {
            int(mois): float(total)
            for mois, total in results
        }

    def detect_duplicates(self, transaction_data: TransactionCreate) -> List[Transaction]:  # Détecte doublons potentiels
        return self.db.query(Transaction).filter(
            and_(
                Transaction.date == transaction_data.date,
                Transaction.montant == transaction_data.montant,
                Transaction.libelle == transaction_data.libelle,
                Transaction.sci_id == transaction_data.sci_id
            )
        ).all()
