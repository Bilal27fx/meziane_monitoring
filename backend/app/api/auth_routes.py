"""
auth_routes.py - Routes API authentification

Description:
Endpoints login, refresh token, profil courant.

Dépendances:
- auth_service.py
- utils.auth.get_current_user

Utilisé par:
- main.py (inclusion router)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from app.utils.db import get_db
from app.utils.auth import get_current_user_db
from app.models.user import User, UserRole
from app.services.auth_service import AuthService, create_access_token, create_refresh_token
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["Auth"])


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


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


def _check_login_rate_limit(username: str):
    """RFC-008: bloque après 5 tentatives échouées en 5 min via Redis"""
    try:
        import redis as _redis
        r = _redis.from_url(settings.REDIS_URL, decode_responses=True)
        key = f"login_attempts:{username}"
        attempts = r.get(key)
        if attempts and int(attempts) >= 5:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Trop de tentatives de connexion. Réessayez dans 5 minutes.",
            )
    except HTTPException:
        raise
    except Exception:
        pass  # Redis indisponible → on laisse passer sans bloquer


def _record_failed_login(username: str):
    try:
        import redis as _redis
        r = _redis.from_url(settings.REDIS_URL, decode_responses=True)
        key = f"login_attempts:{username}"
        pipe = r.pipeline()
        pipe.incr(key)
        pipe.expire(key, 300)  # expire après 5 min
        pipe.execute()
    except Exception:
        pass


def _clear_login_attempts(username: str):
    try:
        import redis as _redis
        r = _redis.from_url(settings.REDIS_URL, decode_responses=True)
        r.delete(f"login_attempts:{username}")
    except Exception:
        pass


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authentification — retourne access + refresh tokens (RFC-008: rate limiting 5 tentatives/5min)"""
    _check_login_rate_limit(form_data.username)
    service = AuthService(db)
    user = service.authenticate(form_data.username, form_data.password)
    if not user:
        _record_failed_login(form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    _clear_login_attempts(form_data.username)
    return TokenResponse(
        access_token=create_access_token(user),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(body: RefreshRequest, db: Session = Depends(get_db)):
    """RFC-008: rotation — chaque refresh émet un nouveau refresh token et révoque l'ancien"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token invalide ou expiré",
    )
    try:
        payload = jwt.decode(body.refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != "refresh":
            raise credentials_exception
        user_id: int = int(payload.get("sub"))
        jti: str = payload.get("jti", "")
    except (JWTError, ValueError):
        raise credentials_exception

    # Vérifie blacklist Redis
    try:
        import redis as _redis
        r = _redis.from_url(settings.REDIS_URL, decode_responses=True)
        if jti and r.get(f"revoked_refresh:{jti}"):
            raise credentials_exception
    except HTTPException:
        raise
    except Exception:
        pass

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise credentials_exception

    # Révoque l'ancien refresh token dans Redis (TTL = durée restante)
    try:
        import redis as _redis
        from app.services.auth_service import REFRESH_TOKEN_EXPIRE_DAYS
        r = _redis.from_url(settings.REDIS_URL, decode_responses=True)
        if jti:
            r.setex(f"revoked_refresh:{jti}", REFRESH_TOKEN_EXPIRE_DAYS * 86400, "1")
    except Exception:
        pass

    return TokenResponse(
        access_token=create_access_token(user),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(body: RefreshRequest):
    """RFC-008: révoque le refresh token dans Redis"""
    try:
        payload = jwt.decode(body.refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
        jti = payload.get("jti", "")
        if jti:
            import redis as _redis
            from app.services.auth_service import REFRESH_TOKEN_EXPIRE_DAYS
            r = _redis.from_url(settings.REDIS_URL, decode_responses=True)
            r.setex(f"revoked_refresh:{jti}", REFRESH_TOKEN_EXPIRE_DAYS * 86400, "1")
    except Exception:
        pass
    return None


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user_db)):
    """Retourne le profil complet — utilise get_current_user_db (seule route qui a besoin de l'ORM)"""
    return current_user
