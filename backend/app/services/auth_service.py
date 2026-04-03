"""
auth_service.py - Service authentification

Description:
Gestion des utilisateurs : création, authentification, tokens JWT.
Hachage bcrypt via passlib.

Dépendances:
- python-jose (JWT)
- passlib[bcrypt]
- models.user

Utilisé par:
- api.auth_routes
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
import bcrypt as _bcrypt
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.config import settings

ACCESS_TOKEN_EXPIRE_MINUTES = 30    # RFC-008: 30 min (était 8h — trop long pour app financière)
REFRESH_TOKEN_EXPIRE_DAYS = 14     # RFC-008: 14 jours avec rotation


def hash_password(password: str) -> str:
    return _bcrypt.hashpw(password.encode("utf-8"), _bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(user: "User", expires_delta: Optional[timedelta] = None) -> str:
    """RFC-008: inclut role dans le payload pour éviter la requête DB par request"""
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {
        "sub": str(user.id),
        "type": "access",
        "exp": expire,
        "role": user.role.value,
        "is_active": user.is_active,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def create_refresh_token(user_id: int) -> str:
    import uuid
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": str(user_id), "type": "refresh", "exp": expire, "jti": str(uuid.uuid4())}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, email: str, password: str, nom: str = None, prenom: str = None, role: UserRole = UserRole.USER) -> "User":
        user = User(
            email=email,
            hashed_password=hash_password(password),
            nom=nom,
            prenom=prenom,
            role=role,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, email: str, password: str) -> Optional[User]:
        user = self.db.query(User).filter(User.email == email, User.is_active == True).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        user.last_login = datetime.utcnow()
        self.db.commit()
        return user

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
