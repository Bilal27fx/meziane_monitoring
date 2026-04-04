from datetime import date

from app.models.bail import Bail, StatutBail
from app.models.bien import Bien, StatutBien, TypeBien
from app.models.locataire import Locataire
from app.models.quittance import Quittance, StatutQuittance
from app.models.sci import SCI
from app.services.patrimoine_service import PatrimoineService
from app.schemas.locataire_schema import LocataireUpdate


def test_get_all_sci_uses_aggregated_read_model(monkeypatch, db_session):
    class FrozenDate(date):
        @classmethod
        def today(cls):
            return cls(2026, 3, 25)

    monkeypatch.setattr("app.queries.patrimoine_queries.date", FrozenDate)

    sci = SCI(nom="SCI Alpha")
    db_session.add(sci)
    db_session.flush()

    bien = Bien(
        sci_id=sci.id,
        adresse="11 boulevard Ornano",
        ville="Paris",
        code_postal="75018",
        type_bien=TypeBien.APPARTEMENT,
        prix_acquisition=120000,
        valeur_actuelle=140000,
        statut=StatutBien.LOUE,
    )
    db_session.add(bien)
    db_session.flush()

    locataire = Locataire(nom="Slimani", prenom="Houcine", email="houcine@example.com")
    db_session.add(locataire)
    db_session.flush()

    db_session.add(
        Bail(
            bien_id=bien.id,
            locataire_id=locataire.id,
            date_debut=FrozenDate(2025, 10, 1),
            loyer_mensuel=780,
            charges_mensuelles=70,
            statut=StatutBail.ACTIF,
        )
    )
    db_session.commit()

    items, total = PatrimoineService(db_session).get_all_sci()

    assert total == 1
    assert len(items) == 1
    assert items[0].nb_biens == 1
    assert items[0].valeur_totale == 140000
    assert items[0].cashflow_mensuel == 850


def test_get_all_biens_returns_joined_read_data(monkeypatch, db_session):
    class FrozenDate(date):
        @classmethod
        def today(cls):
            return cls(2026, 3, 25)

    monkeypatch.setattr("app.queries.patrimoine_queries.date", FrozenDate)

    sci = SCI(nom="SCI Beta")
    db_session.add(sci)
    db_session.flush()

    bien = Bien(
        sci_id=sci.id,
        adresse="8 rue de Paris",
        ville="Lyon",
        code_postal="69001",
        type_bien=TypeBien.STUDIO,
        prix_acquisition=100000,
        statut=StatutBien.LOUE,
    )
    db_session.add(bien)
    db_session.flush()

    locataire = Locataire(nom="Martin", prenom="Lina", email="lina@example.com")
    db_session.add(locataire)
    db_session.flush()

    bail = Bail(
        bien_id=bien.id,
        locataire_id=locataire.id,
        date_debut=FrozenDate(2026, 1, 1),
        loyer_mensuel=700,
        charges_mensuelles=100,
        statut=StatutBail.ACTIF,
    )
    db_session.add(bail)
    db_session.flush()

    db_session.add(
        Quittance(
            bail_id=bail.id,
            mois=3,
            annee=2026,
            montant_loyer=700,
            montant_charges=100,
            montant_total=800,
            statut=StatutQuittance.PAYE,
        )
    )
    db_session.commit()

    items, total = PatrimoineService(db_session).get_all_biens()

    assert total == 1
    assert len(items) == 1
    assert items[0].sci_nom == "SCI Beta"
    assert items[0].loyer_mensuel == 800
    assert items[0].tri_net == 9.6
    assert items[0].statut_paiement == "a_jour"


def test_get_all_locataires_returns_active_bail_read_data(monkeypatch, db_session):
    class FrozenDate(date):
        @classmethod
        def today(cls):
            return cls(2026, 3, 25)

    monkeypatch.setattr("app.queries.patrimoine_queries.date", FrozenDate)

    sci = SCI(nom="SCI Gamma")
    db_session.add(sci)
    db_session.flush()

    bien = Bien(
        sci_id=sci.id,
        adresse="25 avenue Victor Hugo",
        ville="Paris",
        code_postal="75016",
        type_bien=TypeBien.APPARTEMENT,
        statut=StatutBien.LOUE,
    )
    db_session.add(bien)
    db_session.flush()

    locataire = Locataire(nom="Benali", prenom="Amine", email="amine@example.com")
    db_session.add(locataire)
    db_session.flush()

    bail = Bail(
        bien_id=bien.id,
        locataire_id=locataire.id,
        date_debut=FrozenDate(2025, 11, 1),
        loyer_mensuel=900,
        charges_mensuelles=50,
        statut=StatutBail.ACTIF,
    )
    db_session.add(bail)
    db_session.flush()

    db_session.add(
        Quittance(
            bail_id=bail.id,
            mois=3,
            annee=2026,
            montant_loyer=900,
            montant_charges=50,
            montant_total=950,
            statut=StatutQuittance.IMPAYE,
        )
    )
    db_session.commit()

    items, total = PatrimoineService(db_session).get_all_locataires()

    assert total == 1
    assert len(items) == 1
    assert items[0].bien_id == bien.id
    assert items[0].bail is not None
    assert items[0].bail.bien_adresse == "25 avenue Victor Hugo"
    assert items[0].statut_paiement == "impaye"


def test_update_locataire_resyncs_paid_quittances(db_session):
    sci = SCI(nom="SCI Delta")
    db_session.add(sci)
    db_session.flush()

    bien = Bien(
        sci_id=sci.id,
        adresse="12 rue des Fleurs",
        ville="Paris",
        code_postal="75010",
        type_bien=TypeBien.APPARTEMENT,
        statut=StatutBien.LOUE,
    )
    db_session.add(bien)
    db_session.flush()

    locataire = Locataire(nom="Slimani", prenom="Houcine", email="houcine@example.com")
    db_session.add(locataire)
    db_session.flush()

    bail = Bail(
        bien_id=bien.id,
        locataire_id=locataire.id,
        date_debut=date(2025, 1, 1),
        date_fin=date(2027, 1, 1),
        loyer_mensuel=850,
        charges_mensuelles=0,
        statut=StatutBail.ACTIF,
    )
    db_session.add(bail)
    db_session.flush()

    quittance = Quittance(
        bail_id=bail.id,
        mois=3,
        annee=2026,
        montant_loyer=850,
        montant_charges=0,
        montant_total=850,
        statut=StatutQuittance.PAYE,
    )
    db_session.add(quittance)
    db_session.commit()

    service = PatrimoineService(db_session)
    service.update_locataire(
        locataire.id,
        LocataireUpdate(
            bail={
                "bien_id": bien.id,
                "date_debut": date(2025, 1, 1),
                "date_fin": date(2027, 1, 1),
                "loyer_mensuel": 780,
                "charges_mensuelles": 70,
                "depot_garantie": None,
            }
        ),
    )

    db_session.refresh(quittance)
    assert quittance.montant_loyer == 780
    assert quittance.montant_charges == 70
    assert quittance.montant_total == 850
