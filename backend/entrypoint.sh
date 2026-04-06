#!/bin/bash
set -e

echo "[startup] Vérification de l'état de la base de données..."

python3 - <<'EOF'
import sys, os

try:
    from sqlalchemy import create_engine, text, inspect

    engine = create_engine(os.environ["DATABASE_URL"])
    with engine.connect() as conn:
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        # État corrompu : alembic_version existe mais les tables core sont absentes
        if "alembic_version" in tables and "sci" not in tables:
            print("[startup] État corrompu détecté : alembic_version présente mais tables manquantes.")
            print("[startup] Réinitialisation de alembic_version...")
            conn.execute(text("DELETE FROM alembic_version"))
            conn.commit()
            print("[startup] Réinitialisation effectuée.")
        elif "sci" in tables:
            print(f"[startup] Schéma OK : {len(tables)} tables trouvées.")
        else:
            print("[startup] Base vide, les migrations vont tout créer.")
except Exception as e:
    print(f"[startup] Vérification pré-migration échouée (non bloquant) : {e}")
EOF

echo "[startup] Application des migrations Alembic..."
alembic upgrade head

echo "[startup] Seed des données de base..."
python seed_runner.py

echo "[startup] Démarrage du serveur..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
