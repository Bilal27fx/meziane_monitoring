from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.locataire_schema import BailCreateData


def test_bail_create_data_rejects_end_date_before_start():
    with pytest.raises(ValidationError):
        BailCreateData(
            bien_id=1,
            date_debut=date(2026, 3, 1),
            date_fin=date(2026, 2, 1),
            loyer_mensuel=700,
            charges_mensuelles=100,
        )


def test_bail_create_data_rejects_invalid_ancient_end_date():
    with pytest.raises(ValidationError):
        BailCreateData(
            bien_id=1,
            date_debut=date(2025, 10, 22),
            date_fin=date(8, 10, 22),
            loyer_mensuel=700,
            charges_mensuelles=100,
        )

