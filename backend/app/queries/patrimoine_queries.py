"""
patrimoine_queries.py - Requêtes de lecture optimisées pour le patrimoine
"""

from datetime import date
from typing import List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session, aliased

from app.models.bail import Bail, StatutBail
from app.models.bien import Bien, StatutBien
from app.models.locataire import Locataire
from app.models.quittance import Quittance, StatutQuittance
from app.models.sci import SCI
from app.schemas.bien_schema import BienResponse
from app.schemas.locataire_schema import BailInfo, LocataireResponse
from app.schemas.sci_schema import SCIResponse


def _map_payment_status(quittance: Quittance | None) -> Optional[str]:
    if quittance is None:
        return "a_jour"

    statut_raw = quittance.statut.value if hasattr(quittance.statut, "value") else str(quittance.statut)
    if statut_raw == StatutQuittance.PAYE.value:
        return "a_jour"
    if statut_raw == StatutQuittance.IMPAYE.value:
        return "impaye"
    return "retard"


class PatrimoineQueries:
    def __init__(self, db: Session):
        self.db = db

    def list_sci(self, limit: int = 50, offset: int = 0) -> Tuple[List[SCIResponse], int]:
        total = self.db.query(SCI).count()

        bien_stats = (
            self.db.query(
                Bien.sci_id.label("sci_id"),
                func.count(Bien.id).label("nb_biens"),
                func.sum(Bien.valeur_actuelle).label("valeur_totale"),
            )
            .group_by(Bien.sci_id)
            .subquery()
        )
        cashflow_stats = (
            self.db.query(
                Bien.sci_id.label("sci_id"),
                func.sum(Bail.loyer_mensuel + func.coalesce(Bail.charges_mensuelles, 0)).label("cashflow_mensuel"),
            )
            .join(Bien, Bail.bien_id == Bien.id)
            .filter(Bail.statut == StatutBail.ACTIF)
            .group_by(Bien.sci_id)
            .subquery()
        )

        rows = (
            self.db.query(
                SCI,
                bien_stats.c.nb_biens,
                bien_stats.c.valeur_totale,
                cashflow_stats.c.cashflow_mensuel,
            )
            .outerjoin(bien_stats, bien_stats.c.sci_id == SCI.id)
            .outerjoin(cashflow_stats, cashflow_stats.c.sci_id == SCI.id)
            .order_by(SCI.id.asc())
            .limit(limit)
            .offset(offset)
            .all()
        )

        result = [
            SCIResponse(
                id=sci.id,
                nom=sci.nom,
                forme_juridique=sci.forme_juridique,
                siret=sci.siret,
                date_creation=sci.date_creation,
                capital=sci.capital,
                siege_social=sci.siege_social,
                gerant_nom=sci.gerant_nom,
                gerant_prenom=sci.gerant_prenom,
                nb_biens=int(nb_biens or 0),
                valeur_totale=float(valeur_totale) if valeur_totale is not None else None,
                cashflow_mensuel=float(cashflow_mensuel) if cashflow_mensuel is not None else None,
            )
            for sci, nb_biens, valeur_totale, cashflow_mensuel in rows
        ]
        return result, total

    def list_biens(
        self,
        sci_id: Optional[int] = None,
        statut: Optional[StatutBien] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[BienResponse], int]:
        today = date.today()
        active_bail_ids = (
            self.db.query(
                Bail.bien_id.label("bien_id"),
                func.max(Bail.id).label("bail_id"),
            )
            .filter(Bail.statut == StatutBail.ACTIF)
            .group_by(Bail.bien_id)
            .subquery()
        )
        current_quittance_ids = (
            self.db.query(
                Quittance.bail_id.label("bail_id"),
                func.max(Quittance.id).label("quittance_id"),
            )
            .filter(
                Quittance.mois == today.month,
                Quittance.annee == today.year,
            )
            .group_by(Quittance.bail_id)
            .subquery()
        )

        active_bail = aliased(Bail)
        current_quittance = aliased(Quittance)

        base_query = self.db.query(Bien)
        if sci_id:
            base_query = base_query.filter(Bien.sci_id == sci_id)
        if statut:
            base_query = base_query.filter(Bien.statut == statut)
        total = base_query.count()

        rows = (
            self.db.query(Bien, SCI.nom, active_bail, current_quittance)
            .join(SCI, SCI.id == Bien.sci_id)
            .outerjoin(active_bail_ids, active_bail_ids.c.bien_id == Bien.id)
            .outerjoin(active_bail, active_bail.id == active_bail_ids.c.bail_id)
            .outerjoin(current_quittance_ids, current_quittance_ids.c.bail_id == active_bail.id)
            .outerjoin(current_quittance, current_quittance.id == current_quittance_ids.c.quittance_id)
            .filter(Bien.id.in_(base_query.with_entities(Bien.id)))
            .order_by(Bien.id.asc())
            .limit(limit)
            .offset(offset)
            .all()
        )

        result: list[BienResponse] = []
        for bien, sci_nom, bail_actif, quittance in rows:
            loyer_mensuel = float(bail_actif.loyer_mensuel) if bail_actif and bail_actif.loyer_mensuel is not None else None
            tri_net = None
            if loyer_mensuel and bien.prix_acquisition:
                tri_net = round((loyer_mensuel * 12 / bien.prix_acquisition) * 100, 2)

            statut_paiement = _map_payment_status(quittance) if bail_actif else None

            result.append(
                BienResponse(
                    id=bien.id,
                    sci_id=bien.sci_id,
                    adresse=bien.adresse,
                    ville=bien.ville,
                    code_postal=bien.code_postal,
                    complement_adresse=bien.complement_adresse,
                    type_bien=bien.type_bien,
                    surface=bien.surface,
                    nb_pieces=bien.nb_pieces,
                    etage=bien.etage,
                    date_acquisition=bien.date_acquisition,
                    prix_acquisition=bien.prix_acquisition,
                    valeur_actuelle=bien.valeur_actuelle,
                    dpe_classe=bien.dpe_classe,
                    dpe_date_validite=bien.dpe_date_validite,
                    statut=bien.statut,
                    sci_nom=sci_nom,
                    loyer_mensuel=loyer_mensuel,
                    tri_net=tri_net,
                    statut_paiement=statut_paiement,
                    jours_retard=None,
                )
            )

        return result, total

    def list_locataires(self, limit: int = 50, offset: int = 0) -> Tuple[List[LocataireResponse], int]:
        today = date.today()
        active_bail_ids = (
            self.db.query(
                Bail.locataire_id.label("locataire_id"),
                func.max(Bail.id).label("bail_id"),
            )
            .filter(Bail.statut == StatutBail.ACTIF)
            .group_by(Bail.locataire_id)
            .subquery()
        )
        current_quittance_ids = (
            self.db.query(
                Quittance.bail_id.label("bail_id"),
                func.max(Quittance.id).label("quittance_id"),
            )
            .filter(
                Quittance.mois == today.month,
                Quittance.annee == today.year,
            )
            .group_by(Quittance.bail_id)
            .subquery()
        )

        active_bail = aliased(Bail)
        current_quittance = aliased(Quittance)

        total = self.db.query(Locataire).count()
        rows = (
            self.db.query(Locataire, active_bail, Bien, current_quittance)
            .outerjoin(active_bail_ids, active_bail_ids.c.locataire_id == Locataire.id)
            .outerjoin(active_bail, active_bail.id == active_bail_ids.c.bail_id)
            .outerjoin(Bien, Bien.id == active_bail.bien_id)
            .outerjoin(current_quittance_ids, current_quittance_ids.c.bail_id == active_bail.id)
            .outerjoin(current_quittance, current_quittance.id == current_quittance_ids.c.quittance_id)
            .order_by(Locataire.id.asc())
            .limit(limit)
            .offset(offset)
            .all()
        )

        result: list[LocataireResponse] = []
        for locataire, bail_actif, bien, quittance in rows:
            bail_info = None
            bien_id = None
            statut_paiement = None

            if bail_actif:
                bail_info = BailInfo(
                    id=bail_actif.id,
                    bien_id=bail_actif.bien_id,
                    bien_adresse=bien.adresse if bien else None,
                    loyer_mensuel=bail_actif.loyer_mensuel,
                    charges_mensuelles=bail_actif.charges_mensuelles,
                    depot_garantie=bail_actif.depot_garantie,
                    date_debut=bail_actif.date_debut,
                    date_fin=bail_actif.date_fin,
                    statut=bail_actif.statut.value,
                )
                bien_id = bail_actif.bien_id
                statut_paiement = _map_payment_status(quittance)

            result.append(
                LocataireResponse(
                    id=locataire.id,
                    nom=locataire.nom,
                    prenom=locataire.prenom,
                    email=locataire.email,
                    telephone=locataire.telephone,
                    date_naissance=locataire.date_naissance,
                    profession=locataire.profession,
                    revenus_annuels=locataire.revenus_annuels,
                    bien_id=bien_id,
                    bail=bail_info,
                    statut_paiement=statut_paiement,
                    jours_retard=None,
                )
            )

        return result, total
