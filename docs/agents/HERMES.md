# HERMES — Agent Collecte

**Rôle :** Fetch HTTP + parsing des pages Licitor  
**LLM :** Non  
**Position dans le graphe :** Premier nœud — START → HERMES → [ARCHIVIO, MERCATO]

---

## Responsabilité

HERMES est le seul agent qui touche au réseau.
Il collecte toutes les pages Licitor, détecte la pagination, fetch les pages de détail
de chaque annonce, et transmet les données brutes au reste du graphe.

Il ne prend aucune décision. Il ne fait aucune analyse. Il collecte.

---

## Ce qu'il reçoit (depuis le state)

```python
run_id: int
source_code: str        # "licitor"
session_urls: list[str] # URLs des pages d'audience à traiter
```

---

## Ce qu'il produit (dans le state)

```python
raw_pages: list[dict]
# [
#   {
#     "url": "https://licitor.fr/audience/123",
#     "session_html": "...",
#     "listing_pages": {"https://licitor.fr/annonce/456": "..."},
#     "pdf_urls": {"https://licitor.fr/annonce/456": ["https://.../cahier.pdf"]}
#   }
# ]

raw_listings: list[dict]
# [
#   {
#     "external_id": "456",
#     "source_url": "https://licitor.fr/annonce/456",
#     "title": "Appartement 3P - Paris 11",
#     "reserve_price": 120000.0,
#     "surface_m2": 58.0,
#     "city": "Paris",
#     "postal_code": "75011",
#     "auction_date": "2026-05-15T10:00:00",
#     "tribunal": "TJ Paris",
#     "address": "12 rue de la Roquette",
#     "visit_dates": ["2026-05-01T14:00:00"],
#     "visit_location": "Sur place",
#     "lawyer_name": "Me Dupont",
#     "lawyer_phone": "01 23 45 67 89",
#     "occupancy_status": "libre",
#     "nb_pieces": 3,
#     "surface_balcon_m2": null,
#     "etage": 2,
#     "amenities": {"cave": true, "parking": false, "ascenseur": true}
#   }
# ]
```

---

## Séquence interne

```
1. Pour chaque session_url :
   a. Fetch page principale (HTTP GET)
   b. Détecter pagination (?p=2, ?p=3...)
   c. Fetch pages paginées
   d. Parser les cartes listing → liste d'URLs d'annonces
   e. Fetch page de détail de chaque annonce
   f. Parser chaque page de détail (BeautifulSoup + LLM extraction texte)
   g. Détecter les URLs PDF dans chaque page de détail

2. Construire raw_listings[] et raw_pages[]
3. Logger les erreurs par URL dans state.errors (non-bloquant par annonce)
```

---

## Fichiers

```
backend/app/agents/hermes/
├── __init__.py
├── agent.py        # hermes_node(state) → dict partiel
├── fetcher.py      # HTTP fetch avec retry, timeout, rate limiting
└── parser.py       # BeautifulSoup + extraction structurée
```

---

## Contraintes

- **Rate limiting** : pause entre les requêtes (configurable, défaut 1s)
- **Retry** : 3 tentatives avec backoff exponentiel sur erreur réseau
- **Timeout** : 15s par requête
- **Non-bloquant par annonce** : une erreur sur une URL de détail est loggée, pas fatale
- **Bloquant si 0 listing** : si HERMES ne trouve aucune annonce, le run s'arrête

---

## Adapter pattern (extensibilité multi-source)

HERMES est source-agnostic. Le parsing est délégué à un `SourceAdapter`.

```python
# hermes/fetcher.py
ADAPTERS: dict[str, SourceAdapter] = {
    "licitor": LicitorAdapter(),
    # "certeurop": CerteuropAdapter(),  ← ajouter une source ici
}
```

Chaque adapter implémente :
```python
class SourceAdapter(Protocol):
    def parse_session(self, html: str, url: str) -> RawSession: ...
    def parse_listing_cards(self, html: str, url: str) -> list[RawCard]: ...
    def parse_listing_detail(self, html: str, url: str) -> RawListingDict: ...
    def discover_pdf_urls(self, html: str, url: str) -> list[str]: ...
    def discover_pagination(self, html: str, base_url: str) -> list[str]: ...
```

---

## Erreurs dans le state

```python
# Erreur non-bloquante (une annonce)
{"node": "hermes", "detail": "timeout fetching https://licitor.fr/annonce/789", "ts": "..."}

# Erreur bloquante (0 listing trouvé)
# → Exception levée, run échoue
```
