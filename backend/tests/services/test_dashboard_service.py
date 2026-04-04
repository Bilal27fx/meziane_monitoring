from datetime import date

from sqlalchemy import event

from app.models.bail import Bail, StatutBail
from app.models.bien import Bien, StatutBien, TypeBien
from app.models.locataire import Locataire
from app.models.quittance import Quittance, StatutQuittance
from app.models.sci import SCI
from app.models.transaction import StatutValidation, Transaction, TransactionCategorie
from app.services.dashboard_service import DashboardService


def test_get_recent_transactions_uses_single_select_for_display_data(db_session):
    sci = SCI(nom="SCI Performance")
    db_session.add(sci)
    db_session.flush()

    bien = Bien(
        sci_id=sci.id,
        adresse="15 rue Lecourbe",
        ville="Paris",
        code_postal="75015",
        type_bien=TypeBien.APPARTEMENT,
        statut=StatutBien.LOUE,
    )
    db_session.add(bien)
    db_session.flush()

    db_session.add_all(
        [
            Transaction(
                sci_id=sci.id,
                bien_id=bien.id,
                compte_bancaire_id="acct-1",
                date=date(2026, 3, 25),
                montant=1250,
                libelle="Loyer mars",
                categorie=TransactionCategorie.LOYER,
                statut_validation=StatutValidation.VALIDE,
            ),
            Transaction(
                sci_id=sci.id,
                bien_id=bien.id,
                compte_bancaire_id="acct-1",
                date=date(2026, 3, 24),
                montant=-180,
                libelle="Charges copro",
                categorie=TransactionCategorie.CHARGES_COPRO,
                statut_validation=StatutValidation.EN_ATTENTE,
            ),
        ]
    )
    db_session.commit()

    select_statements: list[str] = []

    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("SELECT"):
            select_statements.append(statement)

    event.listen(db_session.bind, "before_cursor_execute", before_cursor_execute)
    try:
        items = DashboardService(db_session).get_recent_transactions(limit=10)
    finally:
        event.remove(db_session.bind, "before_cursor_execute", before_cursor_execute)

    assert len(items) == 2
    assert items[0]["sci_nom"] == "SCI Performance"
    assert items[0]["bien_adresse"] == "15 rue Lecourbe"
    assert items[0]["statut_validation"] == "valide"
    assert len(select_statements) == 1


def test_get_locataires_overview_returns_total_rent_including_charges(db_session):
    sci = SCI(nom="SCI Dashboard")
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

    locataire = Locataire(nom="Slimani", prenom="Houcine", email="houcine@example.com")
    db_session.add(locataire)
    db_session.flush()

    bail = Bail(
        bien_id=bien.id,
        locataire_id=locataire.id,
        date_debut=date(2025, 10, 1),
        loyer_mensuel=780,
        charges_mensuelles=70,
        statut=StatutBail.ACTIF,
    )
    db_session.add(bail)
    db_session.flush()

    db_session.add(
        Quittance(
            bail_id=bail.id,
            mois=3,
            annee=2026,
            montant_loyer=780,
            montant_charges=70,
            montant_total=850,
            statut=StatutQuittance.PAYE,
        )
    )
    db_session.commit()

    items = DashboardService(db_session).get_locataires_overview()

    assert len(items) == 1
    assert items[0]["loyer_mensuel"] == 850
    assert items[0]["statut_paiement"] == "paye"
