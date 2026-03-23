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
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8   # 8h
REFRESH_TOKEN_EXPIRE_DAYS = 30


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": str(user_id), "type": "access", "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def create_refresh_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": str(user_id), "type": "refresh", "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, email: str, password: str, nom: str = None, prenom: str = None, role: UserRole = UserRole.USER) -> User:
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
