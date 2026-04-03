from datetime import date

from sqlalchemy import event

from app.models.bien import Bien, StatutBien, TypeBien
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
