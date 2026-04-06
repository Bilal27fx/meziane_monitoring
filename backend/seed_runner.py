"""Lance le seed de la base de données."""

from app.utils.db import SessionLocal
from app.utils.seed import run_seed

if __name__ == "__main__":
    db = SessionLocal()
    try:
        run_seed(db)
    finally:
        db.close()
