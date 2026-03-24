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
from app.schemas.sci_schema import SCICreate, SCIUpdate, SCIResponse
from app.schemas.bien_schema import BienCreate, BienUpdate, BienResponse
from app.schemas.locataire_schema import LocataireCreate, LocataireUpdate, LocataireResponse, BailInfo


class PatrimoineService:  # Service gestion patrimoine (SCI, Biens, Locataires)

    def __init__(self, db: Session):  # Initialise service avec session DB
        self.db = db

    # === SCI Methods ===

    def get_all_sci(self, limit: int = 50, offset: int = 0) -> Tuple[List[SCIResponse], int]:
        total = self.db.query(SCI).count()
        scis = self.db.query(SCI).limit(limit).offset(offset).all()
        result = []
        for sci in scis:
            biens = self.db.query(Bien).filter(Bien.sci_id == sci.id).all()
            nb_biens = len(biens)
            valeur_totale = sum(b.valeur_actuelle for b in biens if b.valeur_actuelle) or None
            cashflow = 0.0
            for b in biens:
                bail_actif = self.db.query(Bail).filter(
                    Bail.bien_id == b.id,
                    Bail.statut == StatutBail.ACTIF
                ).first()
                if bail_actif:
                    cashflow += bail_actif.loyer_mensuel + bail_actif.charges_mensuelles
            item = SCIResponse(
                id=sci.id,
                nom=sci.nom,
                forme_juridique=sci.forme_juridique,
                siret=sci.siret,
                date_creation=sci.date_creation,
                capital=sci.capital,
                siege_social=sci.siege_social,
                gerant_nom=sci.gerant_nom,
                gerant_prenom=sci.gerant_prenom,
                nb_biens=nb_biens,
                valeur_totale=valeur_totale,
                cashflow_mensuel=cashflow if cashflow > 0 else None,
            )
            result.append(item)
        return result, total

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
        query = self.db.query(Bien)
        if sci_id:
            query = query.filter(Bien.sci_id == sci_id)
        if statut:
            query = query.filter(Bien.statut == statut)
        total = query.count()
        biens = query.limit(limit).offset(offset).all()
        result = []
        for b in biens:
            sci = self.db.query(SCI).filter(SCI.id == b.sci_id).first()
            bail_actif = self.db.query(Bail).filter(
                Bail.bien_id == b.id,
                Bail.statut == StatutBail.ACTIF
            ).first()
            loyer_mensuel = bail_actif.loyer_mensuel if bail_actif else None
            tri_net = None
            if loyer_mensuel and b.prix_acquisition:
                tri_net = round((loyer_mensuel * 12 / b.prix_acquisition) * 100, 2)
            item = BienResponse(
                id=b.id,
                sci_id=b.sci_id,
                adresse=b.adresse,
                ville=b.ville,
                code_postal=b.code_postal,
                complement_adresse=b.complement_adresse,
                type_bien=b.type_bien,
                surface=b.surface,
                nb_pieces=b.nb_pieces,
                etage=b.etage,
                date_acquisition=b.date_acquisition,
                prix_acquisition=b.prix_acquisition,
                valeur_actuelle=b.valeur_actuelle,
                dpe_classe=b.dpe_classe,
                dpe_date_validite=b.dpe_date_validite,
                statut=b.statut,
                sci_nom=sci.nom if sci else None,
                loyer_mensuel=loyer_mensuel,
                tri_net=tri_net,
            )
            result.append(item)
        return result, total

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
                from app.models.quittance import Quittance
                quittance = self.db.query(Quittance).filter(
                    Quittance.bail_id == bail_actif.id,
                    Quittance.mois == today.month,
                    Quittance.annee == today.year,
                ).first()
                if quittance:
                    if quittance.statut == 'payee':
                        statut_paiement = 'a_jour'
                    elif quittance.statut == 'impayee':
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
        total = self.db.query(Locataire).count()
        locataires = self.db.query(Locataire).limit(limit).offset(offset).all()
        result = [self._build_locataire_response(loc) for loc in locataires]
        return result, total

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
