"""
agent.py - Nœud LangGraph ORACLE

Description:
Score multi-dimensionnel déterministe + décision BUY/WATCH/SKIP.
Le LLM est utilisé uniquement pour la justification textuelle (pas le score).
Bloquant global si 0 listing scoré avec succès.

Dépendances:
- oracle/scorer.py
- openai
- app.config

Utilisé par:
- graph/licitor_graph.py (nœud "oracle")
"""

import json
import time
from datetime import datetime, timezone

from app.agents.oracle.scorer import compute_score, DECISION_THRESHOLDS
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

JUSTIFICATION_PROMPT = """Tu expliques la décision d'investissement pour une vente aux enchères judiciaires.
Le score et la décision ont déjà été calculés par l'algorithme. Tu rédiges uniquement la justification en français.

Données du bien :
{listing_summary}

Score : {score}/100 | Décision : {decision}
Breakdown : {breakdown}
Flags : {flags}

Rédige une justification courte (3-5 phrases), factuelle, en français.
Commence directement par les faits — pas de "Ce bien..." ou formule générique.
"""


def _build_justification_prompt(listing: dict, scored: dict, price_est: dict | None) -> str:
    summary = {
        "titre": listing.get("title", ""),
        "ville": listing.get("city", ""),
        "surface_m2": listing.get("surface_m2"),
        "reserve_price": listing.get("reserve_price"),
        "occupation": listing.get("occupancy_status"),
        "prix_m2_marche": (price_est or {}).get("prix_m2_marche"),
        "ratio": (price_est or {}).get("ratio"),
    }
    return JUSTIFICATION_PROMPT.format(
        listing_summary=json.dumps(summary, ensure_ascii=False, indent=2),
        score=scored["score"],
        decision=scored["decision"],
        breakdown=json.dumps(scored["breakdown"], ensure_ascii=False),
        flags=scored["flags"],
    )


def _get_llm_justification(prompt: str, listing_url: str) -> tuple[str, int]:
    """Appelle gpt-4o pour générer la justification. Retourne (texte, tokens)."""
    if not settings.OPENAI_API_KEY:
        return "Justification indisponible (OPENAI_API_KEY absent).", 0
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.3,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
            timeout=20,
        )
        text = resp.choices[0].message.content.strip()
        tokens = resp.usage.total_tokens if resp.usage else 0
        return text, tokens
    except Exception as exc:
        logger.warning(f"[ORACLE] LLM justification failed for {listing_url}: {exc}")
        return "Justification indisponible.", 0


def oracle_node(state: dict) -> dict:
    """Nœud ORACLE — score + décision + justification pour chaque listing."""
    raw_listings = state.get("raw_listings", [])
    pdf_extractions = state.get("pdf_extractions", {})
    price_estimates = state.get("price_estimates", {})

    logger.info(f"[ORACLE] {len(raw_listings)} listings à scorer")
    t_start = time.time()

    scored_listings = []
    errors = []
    total_tokens = 0

    for listing in raw_listings:
        listing_url = listing.get("source_url", "")

        # Trouver les données PDF associées à ce listing
        pdf_ext = _find_pdf_for_listing(listing_url, pdf_extractions)

        # Prix marché
        price_est = price_estimates.get(listing_url)

        try:
            scored = compute_score(listing, pdf_ext, price_est)
        except Exception as exc:
            logger.error(f"[ORACLE] compute_score failed {listing_url}: {exc}")
            errors.append({
                "node": "oracle",
                "detail": f"compute_score failed: {exc}",
                "ts": datetime.now(timezone.utc).isoformat(),
            })
            continue

        # Justification LLM — uniquement si pas SKIP par deal breaker
        if scored["decision"] != "SKIP" or not scored["deal_breakers"]:
            prompt = _build_justification_prompt(listing, scored, price_est)
            justification, tokens = _get_llm_justification(prompt, listing_url)
            scored["justification"] = justification
            total_tokens += tokens
        else:
            # SKIP par deal breaker → template fixe, pas de LLM
            scored["justification"] = (
                f"Bien éliminé : {', '.join(scored['deal_breakers'])}. "
                "Score = 0, décision automatique SKIP."
            )

        scored_listings.append(scored)

    if not scored_listings:
        raise RuntimeError("[ORACLE] 0 listing scoré avec succès — run échoue.")

    duration_ms = int((time.time() - t_start) * 1000)
    buy_count = sum(1 for s in scored_listings if s["decision"] == "BUY")
    watch_count = sum(1 for s in scored_listings if s["decision"] == "WATCH")
    logger.info(
        f"[ORACLE] {len(scored_listings)} scorés en {duration_ms}ms — "
        f"BUY:{buy_count} WATCH:{watch_count} SKIP:{len(scored_listings)-buy_count-watch_count}"
    )

    return {
        "scored_listings": scored_listings,
        "errors": errors,
        "token_usage": {"oracle": total_tokens},
        "durations_ms": {"oracle": duration_ms},
    }


def _find_pdf_for_listing(listing_url: str, pdf_extractions: dict) -> dict | None:
    """Cherche l'extraction PDF correspondant à un listing_url."""
    for pdf_url, extraction in pdf_extractions.items():
        if extraction and extraction.get("listing_url") == listing_url:
            return extraction
    return None
