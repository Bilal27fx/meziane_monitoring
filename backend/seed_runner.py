"""Lance le seed de la base de données."""

from app.models import load_all_models
from app.utils.db import SessionLocal
from app.utils.seed import run_seed

load_all_models()

if __name__ == "__main__":
    db = SessionLocal()
    try:
        run_seed(db)
    finally:
        db.close()
