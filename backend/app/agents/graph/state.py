"""
state.py - AuctionGraphState — état partagé du graphe LangGraph

Description:
TypedDict unique qui circule entre tous les nœuds du graphe.
Chaque nœud ne retourne que les clés qu'il a remplies.

Dépendances:
- typing

Utilisé par:
- graph/licitor_graph.py
- agents/hermes/agent.py
- agents/archivio/agent.py
- agents/mercato/agent.py
- agents/oracle/agent.py
- agents/persist/agent.py
"""

from typing import TypedDict, Annotated
import operator


def _merge_dict(a: dict, b: dict) -> dict:  # Fusionner deux dicts sans écraser
    return {**a, **b}


class AuctionGraphState(TypedDict):

    # ── Input ──────────────────────────────────────────────
    run_id: int
    source_code: str            # "licitor" | "certeurop" | ...
    session_urls: list[str]

    # ── HERMES output ──────────────────────────────────────
    raw_pages: list[dict]
    # [{url, session_html, listing_pages: {url: html}, pdf_urls: {url: [str]}}]
    raw_listings: list[dict]
    # [{external_id, source_url, title, reserve_price, surface_m2, city,
    #   postal_code, auction_date, tribunal, address, visit_dates, ...}]

    # ── ARCHIVIO output (fan-out merge) ────────────────────
    pdf_extractions: Annotated[dict, _merge_dict]
    # pdf_url → {listing_url, surface_m2, charges_annuelles, dpe_classe, ...}

    # ── MERCATO output ─────────────────────────────────────
    price_estimates: dict
    # listing_url → {prix_m2_marche, ratio, nb_transactions, source, confidence}

    # ── ORACLE output ──────────────────────────────────────
    scored_listings: list[dict]
    # [{listing_url, score, decision, breakdown, justification, deal_breakers, flags}]

    # ── Meta ───────────────────────────────────────────────
    errors: Annotated[list, operator.add]
    # [{node, detail, ts}]
    token_usage: Annotated[dict, _merge_dict]
    # {"archivio": 1240, "oracle": 2100}
    durations_ms: Annotated[dict, _merge_dict]
    # {"hermes": 4200, "archivio": 8100}
