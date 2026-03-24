"""
Script de seed — crée l'utilisateur admin par défaut.
Usage : python seed_admin.py
"""
from app.utils.db import SessionLocal
from app.services.auth_service import AuthService
from app.models.user import UserRole

db = SessionLocal()
try:
    service = AuthService(db)
    from app.models.user import User
    from app.services.auth_service import hash_password
    # Met à jour le hash si l'user existe déjà, sinon le crée
    existing = db.query(User).filter(User.email == "admin@meziane.fr").first()
    if existing:
        existing.hashed_password = hash_password("admin1234")
        db.commit()
        print(f"✅ Hash mis à jour : {existing.email}")
    else:
        user = service.create_user(
            email="admin@meziane.fr",
            password="admin1234",
            nom="Meziane",
            prenom="Admin",
            role=UserRole.ADMIN,
        )
        print(f"✅ Admin créé : {user.email} (id={user.id})")
except Exception as e:
    print(f"⚠️  {e}")
finally:
    db.close()
