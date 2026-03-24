"""
auth.py - Dépendances FastAPI pour authentification

Description:
Fournit get_current_user pour protéger les endpoints.
Décode le JWT et charge l'utilisateur depuis la DB.

Dépendances:
- python-jose
- models.user
- utils.db

Utilisé par:
- Tous les *_routes.py (Depends(get_current_user))
"""

from dataclasses import dataclass
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.models.user import User, UserRole
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


@dataclass
class CurrentUser:
    """RFC-008: utilisateur léger depuis JWT — pas de requête DB par request"""
    id: int
    role: UserRole
    is_active: bool


def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    """RFC-008: lit les claims JWT directement, 0 requête DB"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        role_str = payload.get("role")
        is_active = payload.get("is_active", True)
        if user_id is None or role_str is None:
            raise credentials_exception
        if not is_active:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return CurrentUser(id=int(user_id), role=UserRole(role_str), is_active=is_active)


def get_current_user_db(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Charge le User complet depuis DB — utiliser uniquement pour /me ou routes admin qui ont besoin de l'objet ORM"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id), User.is_active == True).first()
    if user is None:
        raise credentials_exception
    return user
