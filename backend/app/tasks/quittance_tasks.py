"""
quittance_tasks.py - Tasks Celery gestion quittances

Description:
Génération mensuelle des quittances de loyer.
Alertes hebdomadaires pour impayés.

Dépendances:
- celery_app
- models (Bail, Quittance, Locataire)
- utils.db

Utilisé par:
- beat_schedule (1er du mois 8h, lundi 9h)
"""

from datetime import datetime
from app.tasks.celery_app import celery_app
from app.utils.db import SessionLocal
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


@celery_app.task(name="app.tasks.quittance_tasks.generate_quittances_task", bind=True)
def generate_quittances_task(self, mois: int = None, annee: int = None):
    """Génère les quittances pour tous les baux actifs du mois"""
    from app.models.bail import Bail, StatutBail
    from app.models.quittance import Quittance, StatutQuittance

    now = datetime.now()
    mois = mois or now.month
    annee = annee or now.year

    logger.info(f"Génération quittances {mois}/{annee}")

    db = SessionLocal()
    try:
        baux_actifs = db.query(Bail).filter(Bail.statut == StatutBail.ACTIF).all()

        created = 0
        skipped = 0

        for bail in baux_actifs:
            # Vérifie si quittance déjà générée
            existing = db.query(Quittance).filter(
                Quittance.bail_id == bail.id,
                Quittance.mois == mois,
                Quittance.annee == annee,
            ).first()

            if existing:
                skipped += 1
                continue

            quittance = Quittance(
                bail_id=bail.id,
                mois=mois,
                annee=annee,
                montant_loyer=bail.loyer_mensuel,
                montant_charges=bail.charges_mensuelles or 0,
                montant_total=bail.loyer_mensuel + (bail.charges_mensuelles or 0),
                statut=StatutQuittance.EN_ATTENTE,
            )
            db.add(quittance)
            created += 1

        db.commit()
        result = {"created": created, "skipped": skipped, "mois": mois, "annee": annee}
        logger.info(f"generate_quittances_task terminé: {result}")
        return result

    except Exception as exc:
        db.rollback()
        logger.error(f"generate_quittances_task échoué: {exc}")
        raise
    finally:
        db.close()


@celery_app.task(name="app.tasks.quittance_tasks.send_alerte_impayes_task", bind=True)
def send_alerte_impayes_task(self):
    """Détecte les impayés et prépare les alertes — job hebdomadaire"""
    from app.models.quittance import Quittance, StatutQuittance
    from app.models.bail import Bail
    from app.models.locataire import Locataire

    logger.info("Démarrage send_alerte_impayes_task")

    db = SessionLocal()
    try:
        impayes = db.query(Quittance).filter(
            Quittance.statut.in_([StatutQuittance.IMPAYE, StatutQuittance.PARTIEL])
        ).all()

        alertes = []
        for q in impayes:
            bail = db.query(Bail).filter(Bail.id == q.bail_id).first()
            if not bail:
                continue
            locataire = db.query(Locataire).filter(Locataire.id == bail.locataire_id).first()
            alertes.append({
                "quittance_id": q.id,
                "locataire": f"{locataire.prenom} {locataire.nom}" if locataire else "Inconnu",
                "email": locataire.email if locataire else None,
                "montant": float(q.montant_total),
                "mois": q.mois,
                "annee": q.annee,
                "statut": q.statut.value,
            })

        logger.info(f"send_alerte_impayes_task: {len(alertes)} impayés détectés")
        # TODO: envoyer emails/WhatsApp via services notification
        return {"nb_impayes": len(alertes), "alertes": alertes}

    except Exception as exc:
        logger.error(f"send_alerte_impayes_task échoué: {exc}")
        raise
    finally:
        db.close()
