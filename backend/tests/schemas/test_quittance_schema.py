from types import SimpleNamespace
from datetime import date

from app.models.quittance import StatutQuittance
from app.schemas.quittance_schema import QuittanceResponse


def test_quittance_response_maps_model_to_frontend_shape():
    bail = SimpleNamespace(locataire_id=7)
    quittance = SimpleNamespace(
        id=12,
        bail=bail,
        mois=3,
        annee=2026,
        montant_total=850.0,
        statut=StatutQuittance.PAYE,
        date_paiement=date(2026, 3, 5),
    )

    response = QuittanceResponse.model_validate(quittance)

    assert response.locataire_id == 7
    assert response.mois == "mars 2026"
    assert response.montant == 850.0
    assert response.statut == "payee"
    assert response.created_at == ""

