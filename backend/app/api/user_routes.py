"""
user_routes.py - Routes API gestion Utilisateurs

Description:
Endpoints CRUD pour les utilisateurs (admin uniquement).
Création, liste, mise à jour du rôle, suppression.

Dépendances:
- auth_service.py
- models.user

Utilisé par:
- main.py (inclusion router)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from app.utils.db import get_db
from app.utils.auth import get_current_user
from app.models.user import User, UserRole
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/users", tags=["Users"])


class UserResponse(BaseModel):
    id: int
    email: str
    nom: Optional[str]
    prenom: Optional[str]
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nom: Optional[str] = None
    prenom: Optional[str] = None
    role: UserRole = UserRole.USER


class UserUpdate(BaseModel):
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs"
        )
    return current_user


@router.get("/", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):  # Liste tous les utilisateurs (admin uniquement)
    return db.query(User).order_by(User.created_at).all()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):  # Crée un nouvel utilisateur (admin uniquement)
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un utilisateur avec cet email existe déjà"
        )
    service = AuthService(db)
    return service.create_user(
        email=data.email,
        password=data.password,
        nom=data.nom,
        prenom=data.prenom,
        role=data.role,
    )


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):  # Met à jour rôle/statut d'un utilisateur (admin uniquement)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")
    if user.id == current_user.id and data.role and data.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas rétrograder votre propre compte"
        )
    if data.role is not None:
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.nom is not None:
        user.nom = data.nom
    if data.prenom is not None:
        user.prenom = data.prenom
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):  # Supprime un utilisateur (admin uniquement, ne peut pas se supprimer soi-même)
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas supprimer votre propre compte"
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")
    db.delete(user)
    db.commit()
