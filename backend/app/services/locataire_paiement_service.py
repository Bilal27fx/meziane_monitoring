"""
locataire_paiement_service.py - Service de suivi des paiements locataire
"""

from datetime import date
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models.bail import Bail, StatutBail
from app.models.locataire import Locataire
from app.models.locataire_paiement import LocatairePaiement
from app.models.quittance import Quittance, StatutQuittance
from app.schemas.locataire_paiement_schema import (
    LocatairePaiementCreate,
    LocatairePaiementMonthStatus,
    LocatairePaiementOverviewResponse,
    LocatairePaiementResponse,
    LocatairePaiementYearSummary,
)


class LocatairePaiementService:
    def __init__(self, db: Session):
        self.db = db

    def _get_locataire(self, locataire_id: int) -> Optional[Locataire]:
        return self.db.query(Locataire).filter(Locataire.id == locataire_id).first()

    def _get_reference_bail(self, locataire_id: int) -> Optional[Bail]:
        bail = (
            self.db.query(Bail)
            .filter(Bail.locataire_id == locataire_id, Bail.statut == StatutBail.ACTIF)
            .first()
        )
        if bail:
            return bail
        return (
            self.db.query(Bail)
            .filter(Bail.locataire_id == locataire_id)
            .order_by(Bail.date_debut.desc(), Bail.id.desc())
            .first()
        )

    def _get_effective_bail_end(self, bail: Bail) -> Optional[date]:
        if not bail.date_fin:
            return None
        if bail.date_fin < bail.date_debut:
            return None
        if bail.date_fin.year < 1900:
            return None
        return bail.date_fin

    def _get_target_quittance(self, bail_id: int, quittance_id: Optional[int]) -> Optional[Quittance]:
        if quittance_id:
            return (
                self.db.query(Quittance)
                .options(joinedload(Quittance.bail))
                .filter(Quittance.id == quittance_id, Quittance.bail_id == bail_id)
                .first()
            )

        return (
            self.db.query(Quittance)
            .filter(
                Quittance.bail_id == bail_id,
                Quittance.statut.in_([
                    StatutQuittance.EN_ATTENTE,
                    StatutQuittance.IMPAYE,
                    StatutQuittance.PARTIEL,
                ]),
            )
            .order_by(Quittance.annee.asc(), Quittance.mois.asc(), Quittance.id.asc())
            .first()
            )

    def _get_or_create_quittance_for_period(self, bail: Bail, year: int, month: int) -> Quittance:
        quittance = (
            self.db.query(Quittance)
            .options(joinedload(Quittance.bail))
            .filter(
                Quittance.bail_id == bail.id,
                Quittance.annee == year,
                Quittance.mois == month,
            )
            .first()
        )
        if quittance:
            return quittance

        montant_loyer = float(bail.loyer_mensuel or 0)
        montant_charges = float(bail.charges_mensuelles or 0)
        quittance = Quittance(
            bail_id=bail.id,
            mois=month,
            annee=year,
            montant_loyer=montant_loyer,
            montant_charges=montant_charges,
            montant_total=montant_loyer + montant_charges,
            statut=StatutQuittance.IMPAYE,
        )
        self.db.add(quittance)
        self.db.flush()
        return quittance

    def _sync_quittance_payment_state(self, quittance: Quittance) -> None:
        total_paye = sum(float(p.montant or 0) for p in quittance.paiements)
        quittance.montant_paye = total_paye if total_paye > 0 else None
        quittance.fichier_url = None

        if total_paye <= 0:
            quittance.statut = StatutQuittance.EN_ATTENTE
            quittance.date_paiement = None
            return

        latest_payment = max((p.date_paiement for p in quittance.paiements), default=None)
        quittance.date_paiement = latest_payment

        if total_paye >= float(quittance.montant_total or 0):
            quittance.statut = StatutQuittance.PAYE
            quittance.montant_paye = float(quittance.montant_total or 0)
        else:
            quittance.statut = StatutQuittance.PARTIEL

    def record_payment(
        self,
        locataire_id: int,
        payment_data: LocatairePaiementCreate,
    ) -> Optional[LocatairePaiement]:
        locataire = self._get_locataire(locataire_id)
        if not locataire:
            return None

        bail = self._get_reference_bail(locataire_id)
        if not bail:
            return None

        quittance = None
        if payment_data.periode_key:
            try:
                year_str, month_str = payment_data.periode_key.split("-")
                quittance = self._get_or_create_quittance_for_period(bail, int(year_str), int(month_str))
            except ValueError:
                return None
        else:
            quittance = self._get_target_quittance(bail.id, payment_data.quittance_id)

        if payment_data.quittance_id and not quittance:
            return None

        paiement = LocatairePaiement(
            locataire_id=locataire_id,
            bail_id=bail.id,
            quittance_id=quittance.id if quittance else None,
            date_paiement=payment_data.date_paiement,
            montant=payment_data.montant,
            mode_paiement=payment_data.mode_paiement,
            reference=payment_data.reference,
            note=payment_data.note,
        )
        self.db.add(paiement)
        self.db.flush()

        if quittance:
            self.db.refresh(quittance)
            quittance = (
                self.db.query(Quittance)
                .options(joinedload(Quittance.paiements))
                .filter(Quittance.id == quittance.id)
                .first()
            )
            if quittance:
                self._sync_quittance_payment_state(quittance)

        self.db.commit()
        self.db.refresh(paiement)
        return paiement

    def ensure_payment_for_paid_quittance(self, quittance: Quittance) -> LocatairePaiement:
        quittance = (
            self.db.query(Quittance)
            .options(
                joinedload(Quittance.bail),
                joinedload(Quittance.paiements),
            )
            .filter(Quittance.id == quittance.id)
            .first()
        )
        if quittance is None or quittance.bail is None:
            raise ValueError("Quittance invalide")

        existing = (
            self.db.query(LocatairePaiement)
            .filter(LocatairePaiement.quittance_id == quittance.id)
            .order_by(LocatairePaiement.id.desc())
            .first()
        )
        total_deja_paye = sum(float(p.montant or 0) for p in quittance.paiements)
        montant_restant = max(float(quittance.montant_total or 0) - total_deja_paye, 0)

        if montant_restant <= 0:
            self._sync_quittance_payment_state(quittance)
            self.db.commit()
            if existing:
                self.db.refresh(existing)
                return existing
            raise ValueError("Aucun paiement à compléter pour cette quittance")

        paiement = LocatairePaiement(
            locataire_id=quittance.bail.locataire_id,
            bail_id=quittance.bail_id,
            quittance_id=quittance.id,
            date_paiement=quittance.date_paiement or date.today(),
            montant=montant_restant,
        )
        self.db.add(paiement)
        self.db.flush()
        self.db.refresh(quittance)
        quittance = (
            self.db.query(Quittance)
            .options(joinedload(Quittance.paiements))
            .filter(Quittance.id == quittance.id)
            .first()
        )
        if quittance:
            self._sync_quittance_payment_state(quittance)
        self.db.commit()
        self.db.refresh(paiement)
        return paiement

    def get_payment_overview(self, locataire_id: int) -> Optional[LocatairePaiementOverviewResponse]:
        locataire = self._get_locataire(locataire_id)
        if not locataire:
            return None

        bail = self._get_reference_bail(locataire_id)
        if not bail:
            return LocatairePaiementOverviewResponse(locataire_id=locataire_id)

        quittances = (
            self.db.query(Quittance)
            .options(joinedload(Quittance.paiements))
            .filter(Quittance.bail_id == bail.id)
            .order_by(Quittance.annee.desc(), Quittance.mois.desc())
            .all()
        )
        paiements = (
            self.db.query(LocatairePaiement)
            .filter(LocatairePaiement.bail_id == bail.id)
            .order_by(LocatairePaiement.date_paiement.desc(), LocatairePaiement.id.desc())
            .all()
        )

        montant_mensuel = float(bail.loyer_mensuel or 0) + float(bail.charges_mensuelles or 0)
        start = date(bail.date_debut.year, bail.date_debut.month, 1)
        effective_end = self._get_effective_bail_end(bail)
        raw_end = effective_end or date.today()
        capped_end = raw_end if raw_end <= date.today() else date.today()
        end = date(capped_end.year, capped_end.month, 1)

        month_statuses: list[LocatairePaiementMonthStatus] = []
        q_by_key = {f"{q.annee:04d}-{q.mois:02d}": q for q in quittances}

        current = start
        while current <= end:
            key = f"{current.year:04d}-{current.month:02d}"
            label = current.strftime("%m/%Y")
            quittance = q_by_key.get(key)
            montant_du = float(quittance.montant_total) if quittance else montant_mensuel
            montant_paye = 0.0
            paiement_date = None
            statut = "impayee"

            if quittance:
                montant_paye = sum(float(p.montant or 0) for p in quittance.paiements)
                paiement_date = max((p.date_paiement for p in quittance.paiements), default=quittance.date_paiement)
                statut_raw = quittance.statut.value if hasattr(quittance.statut, "value") else str(quittance.statut)
                if statut_raw == StatutQuittance.PAYE.value:
                    statut = "payee"
                    montant_paye = float(quittance.montant_total or 0)
                elif statut_raw == StatutQuittance.PARTIEL.value:
                    statut = "partielle"
                elif statut_raw == StatutQuittance.IMPAYE.value:
                    statut = "impayee"
                else:
                    statut = "en_attente"

            solde = max(montant_du - montant_paye, 0)
            month_statuses.append(
                LocatairePaiementMonthStatus(
                    key=key,
                    label=label,
                    quittance_id=quittance.id if quittance else None,
                    statut=statut,
                    montant_du=montant_du,
                    montant_paye=montant_paye,
                    solde=solde,
                    date_paiement=paiement_date,
                )
            )

            if current.month == 12:
                current = date(current.year + 1, 1, 1)
            else:
                current = date(current.year, current.month + 1, 1)

        total_du = sum(item.montant_du for item in month_statuses)
        total_paye = sum(float(p.montant or 0) for p in paiements)
        mensualites_reglees = sum(1 for item in month_statuses if item.solde <= 0.01)
        mensualites_en_retard = sum(1 for item in month_statuses if item.solde > 0.01)
        yearly_buckets: dict[int, dict[str, float | int]] = {}

        for item in month_statuses:
            annee = int(item.key[:4])
            bucket = yearly_buckets.setdefault(
                annee,
                {
                    "total_du": 0.0,
                    "total_paye": 0.0,
                    "reste_a_payer": 0.0,
                    "mensualites_total": 0,
                    "mensualites_reglees": 0,
                    "mensualites_en_retard": 0,
                },
            )
            bucket["total_du"] += item.montant_du
            bucket["total_paye"] += item.montant_paye
            bucket["reste_a_payer"] += item.solde
            bucket["mensualites_total"] += 1
            if item.solde <= 0.01:
                bucket["mensualites_reglees"] += 1
            else:
                bucket["mensualites_en_retard"] += 1

        resume_annuel = [
            LocatairePaiementYearSummary(
                annee=annee,
                total_du=round(float(bucket["total_du"]), 2),
                total_paye=round(float(bucket["total_paye"]), 2),
                reste_a_payer=round(float(bucket["reste_a_payer"]), 2),
                mensualites_total=int(bucket["mensualites_total"]),
                mensualites_reglees=int(bucket["mensualites_reglees"]),
                mensualites_en_retard=int(bucket["mensualites_en_retard"]),
            )
            for annee, bucket in sorted(yearly_buckets.items(), reverse=True)
        ]

        return LocatairePaiementOverviewResponse(
            locataire_id=locataire_id,
            bail_id=bail.id,
            date_debut_bail=bail.date_debut,
            date_fin_bail=effective_end,
            montant_mensuel=montant_mensuel,
            total_du=round(total_du, 2),
            total_paye=round(total_paye, 2),
            reste_a_payer=round(max(total_du - total_paye, 0), 2),
            mensualites_total=len(month_statuses),
            mensualites_reglees=mensualites_reglees,
            mensualites_en_retard=mensualites_en_retard,
            paiements=[LocatairePaiementResponse.model_validate(p) for p in paiements[:24]],
            derniers_mois=list(reversed(month_statuses))[:12],
            historique_mensuel=list(reversed(month_statuses)),
            resume_annuel=resume_annuel,
        )
