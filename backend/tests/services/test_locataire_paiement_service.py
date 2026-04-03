from datetime import date as real_date

from app.models.bail import Bail, StatutBail
from app.models.bien import Bien, StatutBien, TypeBien
from app.models.locataire import Locataire
from app.models.locataire_paiement import LocatairePaiement, ModePaiement
from app.models.quittance import Quittance, StatutQuittance
from app.models.sci import SCI
from app.services.locataire_paiement_service import LocatairePaiementService


def test_payment_overview_ignores_invalid_bail_end_date(monkeypatch, db_session):
    class FrozenDate(real_date):
        @classmethod
        def today(cls):
            return cls(2026, 3, 25)

    monkeypatch.setattr("app.services.locataire_paiement_service.date", FrozenDate)

    sci = SCI(nom="SCI Test")
    db_session.add(sci)
    db_session.flush()

    bien = Bien(
        sci_id=sci.id,
        adresse="11 boulevard Ornano",
        ville="Paris",
        code_postal="75018",
        type_bien=TypeBien.APPARTEMENT,
        statut=StatutBien.LOUE,
    )
    db_session.add(bien)
    db_session.flush()

    locataire = Locataire(
        nom="Slimani",
        prenom="Houcine",
        email="houcine@example.com",
    )
    db_session.add(locataire)
    db_session.flush()

    bail = Bail(
        bien_id=bien.id,
        locataire_id=locataire.id,
        date_debut=FrozenDate(2025, 10, 22),
        date_fin=FrozenDate(8, 10, 22),
        loyer_mensuel=780,
        charges_mensuelles=70,
        statut=StatutBail.ACTIF,
    )
    db_session.add(bail)
    db_session.flush()

    quittance = Quittance(
        bail_id=bail.id,
        mois=3,
        annee=2026,
        montant_loyer=780,
        montant_charges=70,
        montant_total=850,
        montant_paye=850,
        date_paiement=FrozenDate(2026, 3, 5),
        statut=StatutQuittance.PAYE,
    )
    db_session.add(quittance)
    db_session.flush()

    paiement = LocatairePaiement(
        locataire_id=locataire.id,
        bail_id=bail.id,
        quittance_id=quittance.id,
        date_paiement=FrozenDate(2026, 3, 5),
        montant=850,
        mode_paiement=ModePaiement.VIREMENT,
    )
    db_session.add(paiement)
    db_session.commit()

    overview = LocatairePaiementService(db_session).get_payment_overview(locataire.id)

    assert overview is not None
    assert overview.bail_id == bail.id
    assert overview.mensualites_total == 6
    assert overview.mensualites_reglees == 1
    assert overview.mensualites_en_retard == 5
    assert overview.reste_a_payer == 4250
    assert [item.key for item in overview.historique_mensuel] == [
        "2026-03",
        "2026-02",
        "2026-01",
        "2025-12",
        "2025-11",
        "2025-10",
    ]
