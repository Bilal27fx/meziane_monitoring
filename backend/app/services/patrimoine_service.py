"""
patrimoine_service.py - Service gestion patrimoine (SCI, Biens)

Description:
Logique métier pour gestion du patrimoine immobilier.
CRUD SCI et Biens avec calculs valeur patrimoniale.

Dépendances:
- models.sci, models.bien
- schemas.sci_schema, schemas.bien_schema
- SQLAlchemy Session

Utilisé par:
- api.sci_routes
- api.bien_routes
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.sci import SCI
from app.models.bien import Bien
from app.models.locataire import Locataire
from app.schemas.sci_schema import SCICreate, SCIUpdate
from app.schemas.bien_schema import BienCreate, BienUpdate
from app.schemas.locataire_schema import LocataireCreate, LocataireUpdate


class PatrimoineService:  # Service gestion patrimoine (SCI, Biens)

    def __init__(self, db: Session):  # Initialise service avec session DB
        self.db = db

    # === SCI Methods ===

    def get_all_sci(self, limit: int = 50, offset: int = 0) -> List[SCI]:  # Récupère toutes les SCI (paginé)
        return self.db.query(SCI).limit(limit).offset(offset).all()

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

    def get_all_biens(self, sci_id: Optional[int] = None, limit: int = 50, offset: int = 0) -> List[Bien]:  # Récupère tous les biens (filtrable par SCI, paginé)
        query = self.db.query(Bien)
        if sci_id:
            query = query.filter(Bien.sci_id == sci_id)
        return query.limit(limit).offset(offset).all()

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

        valeur_totale = self.db.query(Bien.valeur_actuelle).filter(
            Bien.valeur_actuelle.isnot(None)
        ).all()
        valeur_sum = sum([v[0] for v in valeur_totale if v[0]]) if valeur_totale else 0

        return {
            "total_sci": total_sci,
            "total_biens": total_biens,
            "valeur_patrimoniale_totale": valeur_sum
        }

    # === Locataire Methods ===

    def get_all_locataires(self, limit: int = 50, offset: int = 0) -> List[Locataire]:  # Paginé
        return self.db.query(Locataire).limit(limit).offset(offset).all()

    def get_locataire_by_id(self, locataire_id: int) -> Optional[Locataire]:
        return self.db.query(Locataire).filter(Locataire.id == locataire_id).first()

    def create_locataire(self, locataire_data: LocataireCreate) -> Locataire:
        locataire = Locataire(**locataire_data.model_dump())
        self.db.add(locataire)
        self.db.commit()
        self.db.refresh(locataire)
        return locataire

    def update_locataire(self, locataire_id: int, locataire_data: LocataireUpdate) -> Optional[Locataire]:
        locataire = self.get_locataire_by_id(locataire_id)
        if not locataire:
            return None

        update_data = locataire_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(locataire, field, value)

        self.db.commit()
        self.db.refresh(locataire)
        return locataire

    def delete_locataire(self, locataire_id: int) -> bool:
        locataire = self.get_locataire_by_id(locataire_id)
        if not locataire:
            return False

        self.db.delete(locataire)
        self.db.commit()
        return True
