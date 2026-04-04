# Refactor — Fix extraction données Licitor (date, lieu enchère, visite)

**Date :** 2026-04-04  
**Branche :** scoring  
**Statut :** Livré

---

## Problème

L'adapter Licitor ratait fréquemment l'extraction de la date d'enchère et du lieu de visite. 6 bugs identifiés lors du diagnostic.

---

## Fichiers modifiés

| Fichier | Changements |
|---|---|
| `backend/app/agents/auction/adapters/licitor.py` | 5 bugs corrigés (voir détail) |
| `backend/app/models/auction_listing.py` | Fix `@property auction_location` |
| `backend/tests/services/test_licitor_adapter.py` | 6 nouveaux cas de test |

---

## Corrections appliquées

### `licitor.py`

**`_extract_session_datetime`** — retourne `None` au lieu de lever `ValueError`.  
`parse_sessions` gère désormais `None` avec un fallback `external_id` basé sur l'URL.

**`explicit_location_pattern`** — suppression de l'obligation du code postal IDF.  
`[^,\n]` → `[^\n]` pour accepter les adresses avec virgule (ex: "17 av. Jean Lolive, 93500 Pantin").

**`_extract_visit_blocks`** — deux améliorations :  
- Stop keyword `"me "` retiré, remplacé par `avocat_pattern = re.compile(r"\bMe\.?\s+[A-Z][a-z]")` (avec ou sans point après Me).  
- Ajout de `phone_pattern` comme condition d'arrêt supplémentaire pour éviter de capturer les numéros d'avocat dans le bloc visite.  
- Fenêtre de capture : 4 → 6 lignes.

**`_extract_address`** — `"appartement"` retiré des mots-clés d'exclusion.

**`_extract_postal_code`** — accepte tout CP français `1000 <= int(cp) <= 97680` (plus seulement IDF).

### `models/auction_listing.py`

**`@property auction_location`** — retourne `tribunal` seul si `session.city` est absent (au lieu de `None`).

---

## Tests ajoutés

- `test_parse_sessions_returns_none_datetime_when_date_not_found`
- `test_extract_postal_code_works_outside_idf`
- `test_extract_visit_details_location_without_idf_postal_code`
- `test_extract_visit_blocks_not_stopped_by_meme_or_mise`
- `test_extract_visit_blocks_stops_on_avocat_pattern`
- `test_parse_listing_detail_extracts_address_with_appartement_keyword`

Résultat : **17/17 tests passent**.
