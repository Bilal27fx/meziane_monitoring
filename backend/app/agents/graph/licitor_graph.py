"""
licitor_graph.py - Compilation du graphe LangGraph

Description:
Définit la topologie du StateGraph : nœuds, edges, fan-out ARCHIVIO.
Exporte `licitor_graph` compilé, prêt à être invoqué par runner.py.

Dépendances:
- langgraph
- agents/* (tous les nœuds)

Utilisé par:
- graph/runner.py
"""

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from app.agents.graph.state import AuctionGraphState
from app.agents.hermes.agent import hermes_node
from app.agents.archivio.agent import archivio_node
from app.agents.mercato.agent import mercato_node
from app.agents.oracle.agent import oracle_node
from app.agents.persist.agent import persist_node


def _route_after_hermes(state: AuctionGraphState) -> list:
    """Fan-out : envoie une instance ARCHIVIO par PDF + une instance MERCATO."""
    sends = []

    # Fan-out ARCHIVIO : un nœud par PDF détecté
    for raw_page in state.get("raw_pages", []):
        pdf_urls_by_listing: dict = raw_page.get("pdf_urls", {})
        for listing_url, pdf_list in pdf_urls_by_listing.items():
            for pdf_url in pdf_list:
                sends.append(Send("archivio", {
                    "pdf_url": pdf_url,
                    "listing_url": listing_url,
                }))

    # MERCATO : une seule instance reçoit le state complet
    sends.append(Send("mercato", state))

    return sends


# ── Construction du graphe ──────────────────────────────────────────────────
builder = StateGraph(AuctionGraphState)

builder.add_node("hermes", hermes_node)
builder.add_node("archivio", archivio_node)
builder.add_node("mercato", mercato_node)
builder.add_node("oracle", oracle_node)
builder.add_node("persist", persist_node)

builder.add_edge(START, "hermes")
builder.add_conditional_edges("hermes", _route_after_hermes, ["archivio", "mercato"])
builder.add_edge("archivio", "oracle")
builder.add_edge("mercato", "oracle")
builder.add_edge("oracle", "persist")
builder.add_edge("persist", END)

# ── Compilation ─────────────────────────────────────────────────────────────
# checkpointer PostgreSQL : nécessite `pip install langgraph-checkpoint-postgres`
# Désactivé par défaut — activer en prod avec :
#   from langgraph.checkpoint.postgres import PostgresSaver
#   checkpointer = PostgresSaver.from_conn_string(settings.DATABASE_URL)
#   licitor_graph = builder.compile(checkpointer=checkpointer)

from langgraph.checkpoint.memory import MemorySaver
_checkpointer = MemorySaver()

licitor_graph = builder.compile(checkpointer=_checkpointer)
