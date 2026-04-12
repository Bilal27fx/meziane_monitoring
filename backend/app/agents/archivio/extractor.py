"""
extractor.py - Extraction LLM depuis texte PDF

Description:
Extrait le texte brut d'un PDF (pdfplumber) puis appelle gpt-4o-mini
en json_object mode pour structurer les données du cahier des charges.

Dépendances:
- pdfplumber
- openai
- app.config

Utilisé par:
- archivio/agent.py
"""

import io
import json
from app.utils.logger import setup_logger
from app.config import settings

logger = setup_logger(__name__)

PDF_MAX_PAGES = 50
TOKEN_LIMIT = 8000   # tokens prompt max — tronqué si dépassé

EXTRACTION_PROMPT = """Tu analyses le texte d'un cahier des charges ou document immobilier d'une vente aux enchères judiciaires.

Extrais uniquement les informations présentes dans le texte. Si une information est absente, mets null.
Ne déduis jamais une valeur qui n'est pas explicitement dans le texte.

Retourne un JSON avec ces champs:
{
  "surface_m2": float | null,
  "charges_annuelles": float | null,
  "taxe_fonciere": float | null,
  "syndic": string | null,
  "reglement_copropriete": boolean | null,
  "nb_lots_copropriete": integer | null,
  "procedure_syndicale": boolean | null,
  "etat_general": "bon" | "moyen" | "dégradé" | null,
  "dpe_classe": string | null,
  "ges_classe": string | null,
  "amiante": boolean | null,
  "plomb": boolean | null,
  "termites": boolean | null
}

Texte du document:
"""


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extrait le texte brut des 50 premières pages d'un PDF."""
    import pdfplumber
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            pages = pdf.pages[:PDF_MAX_PAGES]
            texts = []
            for page in pages:
                t = page.extract_text()
                if t:
                    texts.append(t)
            return "\n\n".join(texts)
    except Exception as exc:
        logger.warning(f"pdfplumber extraction failed: {exc}")
        return ""


def _truncate_to_token_limit(text: str, max_chars: int = TOKEN_LIMIT * 4) -> str:
    """Tronque le texte à ~max_chars caractères (approximation 1 token ≈ 4 chars)."""
    return text[:max_chars]


def extract_data_with_llm(text: str, pdf_url: str) -> dict:
    """Appelle gpt-4o-mini pour extraire les données structurées du PDF."""
    from openai import OpenAI

    if not settings.OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY absent — extraction LLM ignorée")
        return {}

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    truncated = _truncate_to_token_limit(text)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "user", "content": EXTRACTION_PROMPT + truncated}
            ],
            timeout=30,
        )
        raw_json = response.choices[0].message.content
        result = json.loads(raw_json)
        result["extraction_model"] = "gpt-4o-mini"
        result["raw_text_excerpt"] = text[:500]

        usage = response.usage
        tokens_used = usage.total_tokens if usage else 0
        return result, tokens_used

    except Exception as exc:
        logger.warning(f"LLM extraction failed for {pdf_url}: {exc}")
        return {}, 0


def run_extraction(pdf_bytes: bytes, pdf_url: str, listing_url: str) -> tuple[dict, int]:
    """Pipeline complet : PDF → texte → LLM → données structurées."""
    text = extract_text_from_pdf(pdf_bytes)
    if not text.strip():
        logger.warning(f"Texte vide extrait du PDF: {pdf_url}")
        return {"listing_url": listing_url, "extraction_model": None}, 0

    result, tokens = extract_data_with_llm(text, pdf_url)
    result["listing_url"] = listing_url
    return result, tokens
