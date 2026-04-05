# Plan — Agent Licitor V3 : Extraction LLM-first

**Date :** 2026-04-04  
**Statut :** À valider

---

## Contexte

Le `LicitorAuctionAdapter.parse_listing_detail()` actuel contient ~400 lignes de regex
qui tentent d'extraire les données champ par champ depuis le HTML. Cette approche est
fragile : le texte Licitor utilise du langage naturel ("quatre chambres", "hors balcon
de 3,50 m²", "au 2ème étage"), les regex ratent des variantes, et le code est difficile
à maintenir.

Or les pages Licitor ont **toujours les mêmes sections** — seules les valeurs changent.
C'est le cas d'usage idéal pour segmenter le texte brut et le passer au LLM, qui retourne
un JSON structuré fiable. Un LLM est déjà utilisé en scoring qualitatif — il peut aussi
gérer toute l'extraction du détail annonce.

Exemple de texte Licitor (structure constante) :

```
À l'annexe du Tribunal Judiciaire de Nanterre (Hauts de Seine)
Vente aux enchères publiques en deux lots
jeudi 16 avril 2026 à 14h30

1er lot de la vente
UN STUDIO
de 31,57 m² (hors balcon de 3,50 m²), escalier numéro 6, au 2ème étage
Une cave
Un emplacement de voiture
Mise à prix : 57 000 €

2nd lot de la vente
UN APPARTEMENT
de 103,40 m² (hors terrasses), escalier numéro 6, au 7ème étage...
Mise à prix : 194 000 €

Courbevoie
ZAC Charas Nord
6, rue Kléber

Visite sur place mercredi 8 avril 2026 de 11h30 à 12h30
```

---

## Pipeline cible

```
HTML brut
  ↓ [1] BeautifulSoup → texte brut
  ↓ [2] Segmenteur    → sections nommées (header, lots, address, visit, lawyer)
  ↓ [3] LLM extraction → JSON structuré (LicitorPageExtraction)
  ↓ [4] Persist extraction en DB (LicitorExtraction)
  ↓ [5] Mapper extraction → facts dict → AuctionListing
  ↓ [6] Scoring (inchangé, bénéficie de données plus fiables)
```

---

## Ce qui existe déjà (ne pas toucher)

- `parse_sessions()` et `parse_listing_cards()` dans `licitor.py` — fonctionnent correctement sur les pages index, pas de LLM nécessaire
- `_apply_listing_detail()` dans `auction_ingestion_service.py` — contrat facts dict inchangé
- `score_listing()` dans `auction_scoring_service.py` — inchangé
- Toute la logique de scoring déterministe
- `RawSession`, `RawListing`, `RawListingDetail` dans `base.py`

---

## Périmètre — fichiers modifiés / créés

| Fichier | Action |
|---|---|
| `backend/app/agents/auction/licitor_text_segmenter.py` | Créer |
| `backend/app/agents/auction/licitor_llm_extraction_service.py` | Créer |
| `backend/app/agents/auction/adapters/licitor.py` | Modifier — simplifier `parse_listing_detail`, supprimer méthodes regex détail |
| `backend/app/models/licitor_extraction.py` | Vérifier / compléter |
| `backend/app/services/auction_ingestion_service.py` | Modifier — ajouter persist extraction après `parse_listing_detail` |
| `backend/tests/agents/test_licitor_segmenter.py` | Créer |
| `backend/tests/agents/test_licitor_llm_extraction.py` | Créer |

---

## Étapes

### Étape 1 — Segmenteur de texte

**Fichier :** `backend/app/agents/auction/licitor_text_segmenter.py`

Objectif : couper le texte brut en sections nommées, **sans extraire de valeurs**.
Retourne un dataclass `LicitorPageSections` avec :

```python
@dataclass
class LicitorPageSections:
    header: str           # "À l'annexe du Tribunal Judiciaire de Nanterre..."
    auction_block: str    # "Vente aux enchères... jeudi 16 avril 2026 à 14h30"
    lots: list[str]       # un chunk par lot : ["1er lot...", "2nd lot..."]
    address_block: str    # "Courbevoie\nZAC Charas Nord\n6, rue Kléber"
    visit_block: str      # "Visite sur place mercredi 8 avril 2026 de 11h30 à 12h30"
    lawyer_block: str     # "Me. Dupont - 01 23 45 67 89" (vide si absent)
    raw_text: str         # texte intégral (envoyé au LLM en fallback si segmentation échoue)
```

Logique de découpe (marqueurs constants Licitor) :
- **header** : lignes avant "Vente aux enchères" ou premier marqueur de lot
- **auction_block** : bloc autour de la date/heure d'enchère (jour + heure)
- **lots** : split sur `"er lot"`, `"nd lot"`, `"ème lot"` — un chunk par lot
- **address_block** : après les lots, avant "Visite" — lignes qui ressemblent à une adresse
- **visit_block** : lignes contenant "visite" ou "sur place"
- **lawyer_block** : lignes contenant "Me.", "Maître", "avocat"

Testable indépendamment du LLM.

---

### Étape 2 — Modèles Pydantic d'extraction

**Fichier :** `backend/app/agents/auction/licitor_llm_extraction_service.py` (ou schémas séparés)

```python
class LicitorLotExtraction(BaseModel):
    lot_number: int | None
    type_bien: str | None            # "STUDIO", "APPARTEMENT", "MAISON"
    surface_m2: float | None
    surface_balcon_m2: float | None
    surface_terrasse_m2: float | None
    etage: int | None
    nb_pieces: int | None
    nb_chambres: int | None
    description: str                 # texte brut du lot
    amenities: dict[str, bool]       # cave, parking, box, jardin, ascenseur
    mise_a_prix: float | None
    extras: list[str]                # "débarras", "emplacement voiture"...

class LicitorPageExtraction(BaseModel):
    tribunal: str | None
    city: str | None
    auction_date: str | None         # ISO 8601 : "2026-04-16"
    auction_time: str | None         # "14:30"
    lots: list[LicitorLotExtraction]
    address: str | None
    postal_code: str | None
    visit_dates: list[str]
    visit_location: str | None
    occupancy_status: str | None     # "libre", "occupe", null
    lawyer_name: str | None
    lawyer_phone: str | None
```

---

### Étape 3 — Service LLM extraction

**Fichier :** `backend/app/agents/auction/licitor_llm_extraction_service.py`

```python
def extract_page(sections: LicitorPageSections) -> LicitorPageExtraction:
    ...
```

Prompt envoyé au LLM — chaque section est labellisée :

```
[HEADER]: À l'annexe du Tribunal Judiciaire de Nanterre (Hauts de Seine)
[ENCHÈRE]: Vente aux enchères publiques en deux lots
           jeudi 16 avril 2026 à 14h30
[LOT 1]: UN STUDIO de 31,57 m² (hors balcon de 3,50 m²)...
[LOT 2]: UN APPARTEMENT de 103,40 m²...
[ADRESSE]: Courbevoie, ZAC Charas Nord, 6 rue Kléber
[VISITE]: Visite sur place mercredi 8 avril 2026 de 11h30 à 12h30
```

Config technique :
- Réutilise `OPENAI_API_KEY` + même client OpenAI que `auction_scoring_service.py`
- `response_format={"type": "json_object"}`
- Modèle : `gpt-4o-mini` (suffisant pour extraction structurée)
- Validation Pydantic sur la réponse

Prompt système :
> "Tu es un extracteur de données d'annonces de ventes judiciaires françaises.
> À partir des sections de texte brut fournies, extrais les informations dans le format
> JSON demandé. Ne devine pas les données absentes — utilise null si l'information
> n'est pas dans le texte. Dates en ISO 8601, surfaces en float, prix en float sans €."

Gestion des erreurs :
| Situation | Comportement |
|---|---|
| LLM indisponible | Fallback regex (méthodes conservées dans `licitor.py`) |
| LLM timeout | Retry 1x, puis fallback regex |
| JSON invalide (ValidationError) | Log warning + fallback regex |
| Segmentation échouée | Envoyer `raw_text` complet sans labels |

---

### Étape 4 — Modifier `parse_listing_detail` dans `licitor.py`

Remplacer le corps de `parse_listing_detail` par :

```python
def parse_listing_detail(self, html: str, page_url: str, listing: RawListing) -> RawListingDetail:
    soup = BeautifulSoup(html, "html.parser")
    raw_text = soup.get_text("\n", strip=True)

    try:
        sections = segment_licitor_page(raw_text)
        extraction = extract_page(sections)
        lot = self._match_lot(extraction.lots, listing)
        facts = self._map_extraction_to_facts(extraction, lot)
        facts["raw_llm_extraction"] = extraction.model_dump()
        facts["documents"] = self._extract_documents(soup, page_url)
    except Exception:
        logger.warning("LLM extraction failed for %s — fallback regex", page_url)
        facts = self._extract_facts_regex(soup, raw_text, page_url, listing)

    return RawListingDetail(listing=listing, facts=facts)
```

`_match_lot()` : matche le lot correspondant à `listing.source_url` ou `listing.title`
en comparant la mise à prix et la surface (pages multi-lots).

`_map_extraction_to_facts()` : traduit `LicitorPageExtraction` + `LicitorLotExtraction`
vers le dict `facts` attendu par `_apply_listing_detail` (contrat inchangé).

**Méthodes supprimées** de `licitor.py` après validation :
`_extract_floor_info`, `_extract_visit_details`, `_extract_address`,
`_extract_property_details`, `_extract_typology`, `_extract_keyword_signals`,
`_extract_visit_blocks`, `_extract_amenity_presence`, `_is_non_property_line`,
`_is_lawyer_line`

**Méthodes conservées** (utilisées par `parse_sessions` et `parse_listing_cards`) :
`_extract_tribunal`, `_extract_session_datetime`, `_extract_price`,
`_extract_surface`, `_extract_postal_code`, `_extract_city`, `_extract_external_id`,
`_extract_documents`, `_extract_phone`

---

### Étape 5 — Modèle DB `LicitorExtraction`

Vérifier le modèle existant (`licitor_extraction.py`) et s'assurer qu'il couvre :

| Colonne | Type | Description |
|---|---|---|
| `listing_id` | FK | lien vers `AuctionListing` |
| `raw_sections` | JSONB | sections envoyées au LLM |
| `llm_raw_response` | TEXT | réponse brute LLM (debug) |
| `parsed_extraction` | JSONB | `LicitorPageExtraction` sérialisé |
| `extracted_at` | TIMESTAMP | horodatage |
| `extraction_model` | VARCHAR | nom du modèle OpenAI utilisé |

Migration Alembic si des colonnes manquent.

---

### Étape 6 — Modifier `auction_ingestion_service.py`

Dans `ingest_session_page()`, ajouter la persistance extraction juste après `parse_listing_detail` :

```python
detail = self.adapter.parse_listing_detail(detail_html, listing.source_url, raw_listing)
self._persist_licitor_extraction(listing, detail.facts)   # nouveau
self._apply_listing_detail(listing, detail.facts)
```

`_apply_listing_detail` — ajouter la lecture du nouveau champ :

```python
if facts.get("raw_llm_extraction"):
    listing.raw_llm_extraction = facts["raw_llm_extraction"]
```

---

### Ordre d'exécution recommandé

1. Segmenteur (`licitor_text_segmenter.py`) — testable sans LLM
2. Modèles Pydantic (`LicitorLotExtraction`, `LicitorPageExtraction`)
3. Service LLM extraction — tester avec page réelle, vérifier JSON retourné
4. Modifier `licitor.py` — brancher segmenteur + LLM, garder regex en fallback
5. Vérifier modèle DB + migration si nécessaire
6. Modifier `auction_ingestion_service.py` — persist extraction
7. Tests end-to-end sur un run complet

---

## Ce qu'on ne fait PAS

- Pas de modification de `parse_sessions()` ni `parse_listing_cards()` — LLM inutile sur les pages index
- Pas de modification du scoring déterministe
- Pas de changement du contrat `facts` dict consommé par `_apply_listing_detail`
- Pas de suppression des méthodes regex avant que le LLM soit validé en prod
- Pas de décision sur multi-lots sans validation Bilal (voir questions ci-dessous)

---

## Questions à valider avant de coder

1. **Multi-lots** : page avec N lots → créer N `AuctionListing` distincts ou garder 1 listing avec les lots dans `property_details` ?
2. **Fallback regex** : conserver indéfiniment ou supprimer après stabilisation LLM ?
3. **Quel LLM** : réutiliser `OPENAI_API_KEY` + `gpt-4o-mini` ou passer à Claude API (`claude-haiku-4-5`) ?

---

## Tests attendus

| Test | Type | Description |
|---|---|---|
| `test_segment_multi_lot_page` | Unitaire | Segmenteur découpe correctement l'exemple à 2 lots |
| `test_segment_single_lot_page` | Unitaire | Segmenteur sur page avec 1 seul lot |
| `test_segment_no_visit_block` | Unitaire | Page sans visite → `visit_block` vide, pas d'erreur |
| `test_llm_extraction_returns_valid_pydantic` | Unitaire | Mock OpenAI → JSON → `LicitorPageExtraction` validé |
| `test_llm_extraction_invalid_json_raises` | Unitaire | JSON invalide → exception propre |
| `test_parse_listing_detail_uses_llm` | Intégration | LLM mocké, `facts` correctement peuplé |
| `test_parse_listing_detail_fallback_on_llm_failure` | Intégration | LLM down → fallback regex s'active |
| `test_match_lot_by_reserve_price` | Unitaire | `_match_lot` trouve le bon lot sur mise à prix |
