"""
patrimoine_service.py - Service gestion patrimoine (SCI, Biens, Locataires)

Description:
Logique métier pour gestion du patrimoine immobilier.
CRUD SCI, Biens et Locataires avec calculs valeur patrimoniale.

Dépendances:
- models.sci, models.bien, models.locataire, models.bail
- schemas.sci_schema, schemas.bien_schema, schemas.locataire_schema
- SQLAlchemy Session

Utilisé par:
- api.sci_routes
- api.bien_routes
- api.locataire_routes
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Tuple
from datetime import date
from app.models.sci import SCI
from app.models.bien import Bien, StatutBien
from app.models.locataire import Locataire
from app.models.bail import Bail, StatutBail
from app.models.quittance import Quittance, StatutQuittance
from app.queries.patrimoine_queries import PatrimoineQueries
from app.schemas.sci_schema import SCICreate, SCIUpdate, SCIResponse
from app.schemas.bien_schema import BienCreate, BienUpdate, BienResponse
from app.schemas.locataire_schema import LocataireCreate, LocataireUpdate, LocataireResponse, BailInfo


class PatrimoineService:  # Service gestion patrimoine (SCI, Biens, Locataires)

    def __init__(self, db: Session):  # Initialise service avec session DB
        self.db = db

    # === SCI Methods ===

    def get_all_sci(self, limit: int = 50, offset: int = 0) -> Tuple[List[SCIResponse], int]:
        return PatrimoineQueries(self.db).list_sci(limit=limit, offset=offset)

    def get_sci_by_id(self, sci_id: int) -> Optional[SCI]:  # Récupère SCI par ID
        return self.db.query(SCI).filter(SCI.id == sci_id).first()

    def create_sci(self, sci_data: SCICreate) -> SCI:  # Crée nouvelle SCI
        sci = SCI(**sci_data.model_dump())
        self.db.add(sci)
        self.db.commit()
        self.db.refresh(sci)
        return sci

    def update_sci(self, sci_id: int, sci_data: SCIUpdate) -> Optional[SCI]:  # Met à jour SCI existante
        sci = self.get_sci_by_id(sci_id)
        if not sci:
            return None
        update_data = sci_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(sci, field, value)
        self.db.commit()
        self.db.refresh(sci)
        return sci

    def delete_sci(self, sci_id: int) -> bool:  # Supprime SCI par ID
        sci = self.get_sci_by_id(sci_id)
        if not sci:
            return False
        self.db.delete(sci)
        self.db.commit()
        return True

    # === Bien Methods ===

    def get_all_biens(self, sci_id: Optional[int] = None, statut: Optional[StatutBien] = None, limit: int = 50, offset: int = 0) -> Tuple[List[BienResponse], int]:
        return PatrimoineQueries(self.db).list_biens(
            sci_id=sci_id,
            statut=statut,
            limit=limit,
            offset=offset,
        )

    def get_bien_by_id(self, bien_id: int) -> Optional[Bien]:  # Récupère bien par ID
        return self.db.query(Bien).filter(Bien.id == bien_id).first()

    def create_bien(self, bien_data: BienCreate) -> Bien:  # Crée nouveau bien immobilier
        bien = Bien(**bien_data.model_dump())
        self.db.add(bien)
        self.db.commit()
        self.db.refresh(bien)
        return bien

    def update_bien(self, bien_id: int, bien_data: BienUpdate) -> Optional[Bien]:  # Met à jour bien existant
        bien = self.get_bien_by_id(bien_id)
        if not bien:
            return None
        update_data = bien_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(bien, field, value)
        self.db.commit()
        self.db.refresh(bien)
        return bien

    def delete_bien(self, bien_id: int) -> bool:  # Supprime bien par ID
        bien = self.get_bien_by_id(bien_id)
        if not bien:
            return False
        self.db.delete(bien)
        self.db.commit()
        return True

    # === Analytics Methods ===

    def get_patrimoine_stats(self) -> dict:  # Calcule statistiques patrimoine global
        total_sci = self.db.query(SCI).count()
        total_biens = self.db.query(Bien).count()
        valeur_totale = self.db.query(func.sum(Bien.valeur_actuelle)).scalar() or 0
        return {
            "total_sci": total_sci,
            "total_biens": total_biens,
            "valeur_patrimoniale_totale": valeur_totale
        }

    # === Locataire Methods ===

    def _build_locataire_response(self, locataire: Locataire) -> LocataireResponse:
        bail_actif = self.db.query(Bail).filter(
            Bail.locataire_id == locataire.id,
            Bail.statut == StatutBail.ACTIF
        ).first()
        bail_info = None
        bien_id = None
        statut_paiement = None
        jours_retard = None
        if bail_actif:
            bien = self.db.query(Bien).filter(Bien.id == bail_actif.bien_id).first()
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
            today = date.today()
            try:
                quittance = self.db.query(Quittance).filter(
                    Quittance.bail_id == bail_actif.id,
                    Quittance.mois == today.month,
                    Quittance.annee == today.year,
                ).first()
                if quittance:
                    statut_raw = quittance.statut.value if hasattr(quittance.statut, "value") else str(quittance.statut)
                    if statut_raw == StatutQuittance.PAYE.value:
                        statut_paiement = 'a_jour'
                    elif statut_raw == StatutQuittance.IMPAYE.value:
                        statut_paiement = 'impaye'
                        if hasattr(quittance, 'date_echeance') and quittance.date_echeance:
                            jours_retard = (today - quittance.date_echeance).days
                    else:
                        statut_paiement = 'retard'
                else:
                    statut_paiement = 'a_jour'
            except Exception:
                statut_paiement = 'a_jour'

        return LocataireResponse(
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
            jours_retard=jours_retard,
        )

    def get_all_locataires(self, limit: int = 50, offset: int = 0) -> Tuple[List[LocataireResponse], int]:
        return PatrimoineQueries(self.db).list_locataires(limit=limit, offset=offset)

    def get_locataire_by_id(self, locataire_id: int) -> Optional[LocataireResponse]:
        locataire = self.db.query(Locataire).filter(Locataire.id == locataire_id).first()
        if not locataire:
            return None
        return self._build_locataire_response(locataire)

    def create_locataire(self, locataire_data: LocataireCreate) -> LocataireResponse:
        bail_data = locataire_data.bail
        locataire_dict = locataire_data.model_dump(exclude={'bail'})
        locataire = Locataire(**locataire_dict)
        self.db.add(locataire)
        self.db.flush()
        if bail_data:
            bail = Bail(
                locataire_id=locataire.id,
                bien_id=bail_data.bien_id,
                date_debut=bail_data.date_debut,
                date_fin=bail_data.date_fin,
                loyer_mensuel=bail_data.loyer_mensuel,
                charges_mensuelles=bail_data.charges_mensuelles,
                depot_garantie=bail_data.depot_garantie,
                statut=StatutBail.ACTIF,
            )
            self.db.add(bail)
        self.db.commit()
        self.db.refresh(locataire)
        return self._build_locataire_response(locataire)

    def _sync_quittances_for_bail(self, bail_id: int, loyer_mensuel: float, charges_mensuelles: float) -> None:
        total = loyer_mensuel + charges_mensuelles
        quittances = (
            self.db.query(Quittance)
            .filter(
                Quittance.bail_id == bail_id,
                Quittance.statut.in_([
                    StatutQuittance.EN_ATTENTE,
                    StatutQuittance.IMPAYE,
                    StatutQuittance.PARTIEL,
                ]),
            )
            .all()
        )
        for quittance in quittances:
            quittance.montant_loyer = loyer_mensuel
            quittance.montant_charges = charges_mensuelles
            quittance.montant_total = total
            quittance.fichier_url = None

    def update_locataire(self, locataire_id: int, locataire_data: LocataireUpdate) -> Optional[LocataireResponse]:
        locataire = self.db.query(Locataire).filter(Locataire.id == locataire_id).first()
        if not locataire:
            return None
        bail_data = locataire_data.bail
        update_data = locataire_data.model_dump(exclude_unset=True, exclude={'bail'})
        for field, value in update_data.items():
            setattr(locataire, field, value)
        if bail_data:
            bail_actif = self.db.query(Bail).filter(
                Bail.locataire_id == locataire_id,
                Bail.statut == StatutBail.ACTIF
            ).first()
            if bail_actif:
                bail_actif.bien_id = bail_data.bien_id
                bail_actif.date_debut = bail_data.date_debut
                bail_actif.date_fin = bail_data.date_fin
                bail_actif.loyer_mensuel = bail_data.loyer_mensuel
                bail_actif.charges_mensuelles = bail_data.charges_mensuelles
                bail_actif.depot_garantie = bail_data.depot_garantie
                self._sync_quittances_for_bail(
                    bail_id=bail_actif.id,
                    loyer_mensuel=bail_data.loyer_mensuel,
                    charges_mensuelles=bail_data.charges_mensuelles,
                )
            else:
                bail = Bail(
                    locataire_id=locataire_id,
                    bien_id=bail_data.bien_id,
                    date_debut=bail_data.date_debut,
                    date_fin=bail_data.date_fin,
                    loyer_mensuel=bail_data.loyer_mensuel,
                    charges_mensuelles=bail_data.charges_mensuelles,
                    depot_garantie=bail_data.depot_garantie,
                    statut=StatutBail.ACTIF,
                )
                self.db.add(bail)
        self.db.commit()
        self.db.refresh(locataire)
        return self._build_locataire_response(locataire)

    def delete_locataire(self, locataire_id: int) -> bool:
        locataire = self.db.query(Locataire).filter(Locataire.id == locataire_id).first()
        if not locataire:
            return False
        self.db.delete(locataire)
        self.db.commit()
        return True
