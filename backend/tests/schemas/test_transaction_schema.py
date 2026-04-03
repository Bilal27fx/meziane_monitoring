from datetime import date, datetime

from app.models.transaction import StatutValidation, Transaction
from app.schemas.transaction_schema import TransactionResponse


def test_transaction_response_accepts_datetime_created_at():
    transaction = Transaction(
        id=1,
        sci_id=2,
        date=date(2026, 3, 25),
        montant=1250.0,
        libelle="Loyer mars",
        compte_bancaire_id="compte-1",
        statut_validation=StatutValidation.VALIDE,
        created_at=datetime(2026, 3, 25, 10, 30, 0),
    )

    response = TransactionResponse.model_validate(transaction)

    assert response.created_at == datetime(2026, 3, 25, 10, 30, 0)
    assert response.statut == "valide"
    assert response.type == "revenu"


def test_transaction_response_marks_negative_amount_as_depense():
    transaction = Transaction(
        id=2,
        sci_id=3,
        date=date(2026, 3, 25),
        montant=-87.45,
        libelle="Assurance",
        compte_bancaire_id="compte-2",
        statut_validation=StatutValidation.EN_ATTENTE,
        created_at=datetime(2026, 3, 25, 9, 0, 0),
    )

    response = TransactionResponse.model_validate(transaction)

    assert response.type == "depense"
    assert response.statut == "en_attente"

