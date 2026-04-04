"""
quittance_routes.py - Routes API Quittances

Endpoints:
- GET  /api/locataires/{locataire_id}/quittances   liste des quittances d'un locataire
- POST /api/locataires/{locataire_id}/quittances/generer  génère la quittance du mois courant
- GET  /api/quittances/{id}/pdf                    téléchargement PDF (URL de stockage)
"""

import re
import unicodedata
import uuid
from io import BytesIO
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import date

from app.models.quittance import Quittance, StatutQuittance
from app.models.bail import Bail, StatutBail
from app.models.locataire import Locataire
from app.models.bien import Bien
from app.schemas.quittance_schema import QuittanceResponse, QuittanceGenerateResponse
from app.services.locataire_paiement_service import LocatairePaiementService
from app.utils.db import get_db
from app.utils.auth import get_current_user
from app.utils.storage import upload_bytes, get_minio_client
from app.config import settings

router = APIRouter(tags=["Quittances"], dependencies=[Depends(get_current_user)])


def _pdf_text(value: str) -> str:
    return (value or "").encode("cp1252", "replace").decode("cp1252")


def _pdf_escape(value: str) -> str:
    return (
        _pdf_text(value)
        .replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
        .replace("\r", " ")
        .replace("\n", " ")
    )


def _pdf_number(value: float) -> str:
    if isinstance(value, int):
        return str(value)
    return f"{value:.2f}".rstrip("0").rstrip(".")


def _pdf_rgb(r: int, g: int, b: int) -> str:
    return f"{r / 255:.3f} {g / 255:.3f} {b / 255:.3f}"


def _pdf_rect(
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    fill: tuple[int, int, int] | None = None,
    stroke: tuple[int, int, int] | None = None,
    line_width: float = 1,
) -> list[str]:
    commands = ["q", f"{_pdf_number(line_width)} w"]
    if fill is not None:
        commands.append(f"{_pdf_rgb(*fill)} rg")
    if stroke is not None:
        commands.append(f"{_pdf_rgb(*stroke)} RG")
    commands.append(
        f"{_pdf_number(x)} {_pdf_number(y)} {_pdf_number(width)} {_pdf_number(height)} re"
    )
    if fill is not None and stroke is not None:
        commands.append("B")
    elif fill is not None:
        commands.append("f")
    else:
        commands.append("S")
    commands.append("Q")
    return commands


def _pdf_line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    color: tuple[int, int, int],
    line_width: float = 1,
) -> list[str]:
    return [
        "q",
        f"{_pdf_number(line_width)} w",
        f"{_pdf_rgb(*color)} RG",
        f"{_pdf_number(x1)} {_pdf_number(y1)} m",
        f"{_pdf_number(x2)} {_pdf_number(y2)} l",
        "S",
        "Q",
    ]


def _pdf_text_command(
    x: float,
    y: float,
    font_size: int,
    text: str,
    *,
    font: str = "F1",
    color: tuple[int, int, int] = (15, 23, 42),
) -> list[str]:
    return [
        "q",
        f"{_pdf_rgb(*color)} rg",
        "BT",
        f"/{font} {font_size} Tf",
        f"1 0 0 1 {_pdf_number(x)} {_pdf_number(y)} Tm",
        f"({_pdf_escape(text)}) Tj",
        "ET",
        "Q",
    ]


def _wrap_pdf_text(value: str, max_chars: int) -> list[str]:
    words = _pdf_text(value or "-").split()
    if not words:
        return ["-"]

    lines: list[str] = []
    current = ""
    for word in words:
        if len(word) > max_chars:
            if current:
                lines.append(current)
                current = ""
            for start in range(0, len(word), max_chars):
                lines.append(word[start:start + max_chars])
            continue

        candidate = f"{current} {word}".strip()
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)
    return lines or ["-"]


def _format_currency(value: float) -> str:
    return f"{value:,.2f}".replace(",", " ").replace(".", ",") + " EUR"


def _sanitize_filename_part(value: str) -> str:
    cleaned = re.sub(r'[\\/:*?"<>|]+', " ", value or "")
    cleaned = re.sub(r"\s+", "-", cleaned).strip(" .-")
    return cleaned or "Locataire"


def _build_content_disposition(filename: str) -> str:
    ascii_fallback = unicodedata.normalize("NFKD", filename).encode("ascii", "ignore").decode("ascii")
    ascii_fallback = re.sub(r'[\\/:*?"<>|]+', "_", ascii_fallback)
    ascii_fallback = re.sub(r"\s+", "-", ascii_fallback).strip(" .-") or "quittance.pdf"
    return f"attachment; filename=\"{ascii_fallback}\"; filename*=UTF-8''{quote(filename)}"


def _build_pdf_document(commands: list[str]) -> bytes:
    stream = "\n".join(commands).encode("cp1252")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            b"/Resources << /Font << /F1 4 0 R /F2 5 0 R /F3 6 0 R >> >> "
            b"/Contents 7 0 R >>"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique /Encoding /WinAnsiEncoding >>",
        b"<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream),
    ]

    pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_start}\n%%EOF"
        ).encode("ascii")
    )
    return bytes(pdf)


def _resolve_quittance_amounts(quittance: Quittance) -> tuple[float, float, float]:
    if (
        quittance.montant_loyer is not None
        or quittance.montant_charges is not None
        or quittance.montant_total is not None
    ):
        loyer = float(quittance.montant_loyer or 0)
        charges = float(quittance.montant_charges or 0)
        total = float(quittance.montant_total or (loyer + charges))
        return loyer, charges, total

    bail = quittance.bail
    if bail:
        loyer = float(bail.loyer_mensuel or 0)
        charges = float(bail.charges_mensuelles or 0)
        return loyer, charges, loyer + charges
    return (
        float(quittance.montant_loyer or 0),
        float(quittance.montant_charges or 0),
        float(quittance.montant_total or 0),
    )


def _build_bien_full_address(bien: Bien | None) -> str:
    if not bien:
        return "Adresse non renseignée"

    line1_parts = [bien.adresse]
    if bien.complement_adresse:
        line1_parts.append(bien.complement_adresse)
    line1 = ", ".join(part.strip() for part in line1_parts if part and part.strip())

    line2_parts = [bien.code_postal, bien.ville]
    line2 = " ".join(part.strip() for part in line2_parts if part and part.strip())

    full_parts = [part for part in [line1, line2] if part]
    return ", ".join(full_parts) if full_parts else "Adresse non renseignée"


def _build_quittance_pdf(quittance: Quittance) -> bytes:
    bail = quittance.bail
    locataire_nom = "Locataire"
    bien_adresse = "Adresse non renseignée"
    sci_nom = "SCI"
    if bail and bail.locataire:
        locataire_nom = f"{bail.locataire.prenom} {bail.locataire.nom}".strip()
    if bail and bail.bien:
        bien_adresse = _build_bien_full_address(bail.bien)
        if bail.bien.sci:
            sci_nom = bail.bien.sci.nom
    montant_loyer, montant_charges, montant_total = _resolve_quittance_amounts(quittance)

    statut_labels = {
        StatutQuittance.EN_ATTENTE: "En attente",
        StatutQuittance.PAYE: "Payée",
        StatutQuittance.IMPAYE: "Impayée",
        StatutQuittance.PARTIEL: "Paiement partiel",
    }
    statut_label = statut_labels.get(quittance.statut, str(quittance.statut))
    periode = f"{quittance.mois:02d}/{quittance.annee}"
    paiement = quittance.date_paiement.strftime('%d/%m/%Y') if quittance.date_paiement else '-'
    generated_on = date.today().strftime('%d/%m/%Y')
    sci_lines = _wrap_pdf_text(sci_nom, 42)[:2]
    locataire_lines = _wrap_pdf_text(locataire_nom, 42)[:2]
    bien_lines = _wrap_pdf_text(bien_adresse, 78)[:3]

    ink = (28, 37, 48)
    body = (71, 85, 105)
    muted = (100, 116, 139)
    border = (203, 213, 225)
    soft = (248, 250, 252)
    white = (255, 255, 255)

    commands: list[str] = []
    commands.extend(_pdf_rect(40, 40, 515, 762, stroke=border))
    commands.extend(_pdf_line(40, 760, 555, 760, color=ink, line_width=1.2))
    commands.extend(_pdf_text_command(56, 732, 20, "Quittance de loyer", font="F2", color=ink))
    commands.extend(_pdf_text_command(56, 714, 10, "Document locatif", font="F3", color=body))
    commands.extend(_pdf_text_command(420, 732, 10, f"Période : {periode}", font="F1", color=body))
    commands.extend(_pdf_text_command(402, 716, 10, f"Date d'édition : {generated_on}", font="F1", color=body))
    commands.extend(_pdf_line(56, 694, 539, 694, color=border))

    commands.extend(_pdf_text_command(56, 670, 8, "BAILLEUR", font="F2", color=muted))
    commands.extend(_pdf_text_command(310, 670, 8, "LOCATAIRE", font="F2", color=muted))
    for index, line in enumerate(sci_lines):
        commands.extend(_pdf_text_command(56, 648 - (index * 14), 12 if index == 0 else 10, line, font="F2" if index == 0 else "F1", color=ink))
    for index, line in enumerate(locataire_lines):
        commands.extend(_pdf_text_command(310, 648 - (index * 14), 12 if index == 0 else 10, line, font="F2" if index == 0 else "F1", color=ink))
    commands.extend(_pdf_text_command(56, 620, 9, "Société bailleresse", font="F3", color=body))
    commands.extend(_pdf_text_command(310, 620, 9, "Titulaire du bail", font="F3", color=body))

    commands.extend(_pdf_text_command(56, 584, 8, "BIEN LOUÉ", font="F2", color=muted))
    for index, text_line in enumerate(bien_lines):
        commands.extend(_pdf_text_command(56, 562 - (index * 14), 11, text_line, font="F1", color=ink))
    commands.extend(_pdf_line(56, 532, 539, 532, color=border))

    commands.extend(_pdf_rect(56, 486, 483, 24, fill=ink))
    commands.extend(_pdf_text_command(72, 494, 9, "LIBELLÉ", font="F2", color=white))
    commands.extend(_pdf_text_command(330, 494, 9, "MONTANT", font="F2", color=white))
    commands.extend(_pdf_text_command(440, 494, 9, "DÉTAIL", font="F2", color=white))

    row_y = 458
    row_height = 30
    rows = [
        ("Montant réglé", _format_currency(montant_total), f"Paiement : {paiement}"),
        ("Détail", _format_currency(montant_loyer), "Loyer mensuel"),
        ("Charges", _format_currency(montant_charges), "Charges locatives"),
    ]
    for index, (label, amount, detail) in enumerate(rows):
        fill = soft if index % 2 == 0 else white
        commands.extend(_pdf_rect(56, row_y - (index * row_height), 483, row_height, fill=fill, stroke=border))
        y_text = row_y + 11 - (index * row_height)
        amount_font = "F2" if index == 0 else "F1"
        commands.extend(_pdf_text_command(72, y_text, 10, label, font="F1", color=ink))
        commands.extend(_pdf_text_command(330, y_text, 10, amount, font=amount_font, color=ink))
        commands.extend(_pdf_text_command(440, y_text, 9, detail, font="F1", color=body))

    commands.extend(_pdf_rect(56, 322, 483, 66, fill=soft, stroke=border))
    commands.extend(_pdf_text_command(72, 366, 8, "SYNTHÈSE", font="F2", color=muted))
    commands.extend(_pdf_text_command(72, 344, 13, "Montant total réglé", font="F1", color=ink))
    commands.extend(_pdf_text_command(72, 327, 15, _format_currency(montant_total), font="F2", color=ink))
    commands.extend(_pdf_text_command(330, 344, 10, f"Statut : {statut_label}", font="F1", color=body))
    commands.extend(_pdf_text_command(330, 326, 10, f"Date de paiement : {paiement}", font="F1", color=body))

    commands.extend(_pdf_text_command(56, 276, 9, "Attestation", font="F2", color=muted))
    commands.extend(_pdf_line(56, 270, 539, 270, color=border))
    commands.extend(_pdf_text_command(56, 248, 10, "Cette quittance certifie le règlement des sommes dues pour la période indiquée.", font="F1", color=body))
    commands.extend(_pdf_text_command(56, 232, 10, "Elle est établie sur la base des informations du bail et des paiements enregistrés.", font="F1", color=body))

    commands.extend(_pdf_line(56, 108, 539, 108, color=border))
    commands.extend(_pdf_text_command(56, 88, 9, "Meziane Monitoring", font="F2", color=muted))
    commands.extend(_pdf_text_command(56, 74, 9, f"Document édité le {generated_on}", font="F1", color=muted))

    return _build_pdf_document(commands)


def _build_quittance_filename(quittance: Quittance) -> str:
    bail = quittance.bail
    locataire_nom = "Locataire"
    if bail and bail.locataire:
        locataire_nom = f"{bail.locataire.prenom} {bail.locataire.nom}".strip()
    return f"{_sanitize_filename_part(locataire_nom)}-{quittance.annee}-{quittance.mois:02d}.pdf"


def _extract_storage_target(file_url: str) -> tuple[str, str]:
    try:
        parts = file_url.split("/", 4)
        return parts[3], parts[4]
    except (IndexError, AttributeError):
        raise HTTPException(status_code=500, detail="URL PDF quittance invalide")


def _quittance_file_exists(file_url: str) -> bool:
    try:
        bucket_name, object_name = _extract_storage_target(file_url)
        client = get_minio_client()
        client.stat_object(bucket_name, object_name)
        return True
    except Exception:
        return False


@router.get(
    "/api/locataires/{locataire_id}/quittances",
    response_model=List[QuittanceResponse],
)
def get_quittances_locataire(locataire_id: int, db: Session = Depends(get_db)):
    """Liste toutes les quittances d'un locataire, triées par date décroissante."""
    locataire = db.query(Locataire).filter(Locataire.id == locataire_id).first()
    if not locataire:
        raise HTTPException(status_code=404, detail=f"Locataire {locataire_id} introuvable")

    quittances = (
        db.query(Quittance)
        .join(Bail, Bail.id == Quittance.bail_id)
        .filter(Bail.locataire_id == locataire_id)
        .options(joinedload(Quittance.bail))
        .order_by(Quittance.annee.desc(), Quittance.mois.desc())
        .all()
    )
    return quittances


@router.post(
    "/api/locataires/{locataire_id}/quittances/generer",
    response_model=QuittanceGenerateResponse,
    status_code=status.HTTP_201_CREATED,
)
def generer_quittance(locataire_id: int, db: Session = Depends(get_db)):
    """Génère la quittance du mois courant pour le bail actif du locataire."""
    bail_actif = (
        db.query(Bail)
        .filter(Bail.locataire_id == locataire_id, Bail.statut == StatutBail.ACTIF)
        .first()
    )
    if not bail_actif:
        raise HTTPException(
            status_code=404,
            detail=f"Aucun bail actif pour le locataire {locataire_id}"
        )

    today = date.today()
    mois, annee = today.month, today.year

    # Vérifier si la quittance du mois existe déjà
    existante = (
        db.query(Quittance)
        .filter(
            Quittance.bail_id == bail_actif.id,
            Quittance.mois == mois,
            Quittance.annee == annee,
        )
        .first()
    )
    if existante:
        raise HTTPException(
            status_code=409,
            detail=f"Quittance {mois}/{annee} déjà générée (ID: {existante.id})"
        )

    montant_total = bail_actif.loyer_mensuel + bail_actif.charges_mensuelles
    quittance = Quittance(
        bail_id=bail_actif.id,
        mois=mois,
        annee=annee,
        montant_loyer=bail_actif.loyer_mensuel,
        montant_charges=bail_actif.charges_mensuelles,
        montant_total=montant_total,
        statut=StatutQuittance.EN_ATTENTE,
    )
    db.add(quittance)
    db.commit()
    db.refresh(quittance)

    return QuittanceGenerateResponse(
        message=f"Quittance {mois}/{annee} générée",
        quittance_id=quittance.id,
    )


@router.get("/api/quittances/{quittance_id}/pdf")
def get_quittance_pdf(quittance_id: int, db: Session = Depends(get_db)):
    """Genere le PDF a la demande et le stream avec le template courant."""
    quittance = (
        db.query(Quittance)
        .options(
            joinedload(Quittance.bail).joinedload(Bail.locataire),
            joinedload(Quittance.bail).joinedload(Bail.bien).joinedload(Bien.sci),
        )
        .filter(Quittance.id == quittance_id)
        .first()
    )
    if not quittance:
        raise HTTPException(status_code=404, detail=f"Quittance {quittance_id} introuvable")

    montant_loyer, montant_charges, montant_total = _resolve_quittance_amounts(quittance)
    snapshot_changed = (
        quittance.montant_loyer != montant_loyer
        or quittance.montant_charges != montant_charges
        or quittance.montant_total != montant_total
    )
    if snapshot_changed:
        quittance.montant_loyer = montant_loyer
        quittance.montant_charges = montant_charges
        quittance.montant_total = montant_total
        quittance.fichier_url = None
        db.commit()
        db.refresh(quittance)

    pdf_bytes = _build_quittance_pdf(quittance)
    should_upload = not quittance.fichier_url or not _quittance_file_exists(quittance.fichier_url)
    if should_upload:
        try:
            object_name = f"quittances/{quittance.id}/{uuid.uuid4()}_quittance_{quittance.annee}_{quittance.mois:02d}.pdf"
            quittance.fichier_url = upload_bytes(
                bucket_name=settings.MINIO_BUCKET_DOCUMENTS,
                object_name=object_name,
                content=pdf_bytes,
                content_type="application/pdf",
            )
            db.commit()
            db.refresh(quittance)
        except Exception:
            db.rollback()

    filename = _build_quittance_filename(quittance)
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": _build_content_disposition(filename)},
    )


@router.post("/api/quittances/{quittance_id}/payer", response_model=QuittanceResponse)
def mark_quittance_paid(quittance_id: int, db: Session = Depends(get_db)):
    """Marque une quittance comme payée à date du jour."""
    quittance = (
        db.query(Quittance)
        .options(joinedload(Quittance.bail))
        .filter(Quittance.id == quittance_id)
        .first()
    )
    if not quittance:
        raise HTTPException(status_code=404, detail=f"Quittance {quittance_id} introuvable")

    quittance.statut = StatutQuittance.PAYE
    quittance.date_paiement = date.today()
    quittance.montant_paye = quittance.montant_total

    db.commit()
    db.refresh(quittance)
    LocatairePaiementService(db).ensure_payment_for_paid_quittance(quittance)
    db.refresh(quittance)
    return quittance
