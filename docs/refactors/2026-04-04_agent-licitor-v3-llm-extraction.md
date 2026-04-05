# 2026-04-04 — Agent Licitor V3 : Extraction LLM-first

**Commit(s) :** à compléter  
**Plan source :** plans/2026-04-04_agent-licitor-v3-llm-extraction.md

## Changements effectués

Remplacement de l'extraction regex dans `parse_listing_detail` par un pipeline LLM-first :
1. Segmentation du texte brut en sections nommées (`LicitorPageSections`)
2. Appel OpenAI `gpt-4o-mini` en `json_object` mode avec les sections labellisées
3. Validation Pydantic du JSON retourné (`LicitorPageExtraction`)
4. Fallback transparent sur le code regex si LLM indisponible
5. Persistance du JSON extrait dans la table `licitor_extractions`

## Fichiers impactés

| Fichier | Action |
|---|---|
| `backend/app/agents/auction/licitor_text_segmenter.py` | Créé |
| `backend/app/agents/auction/licitor_llm_extraction_service.py` | Créé |
| `backend/app/models/licitor_extraction.py` | Créé |
| `backend/alembic/versions/g8b9c0d1e2f3_add_licitor_extractions_table.py` | Créé |
| `backend/app/agents/auction/adapters/licitor.py` | Modifié — `parse_listing_detail` LLM-first + fallback regex |
| `backend/app/services/auction_ingestion_service.py` | Modifié — import `LicitorExtraction` + persist extraction + `_persist_licitor_extraction` |
| `backend/tests/agents/test_licitor_segmenter.py` | Créé — 21 tests |
| `backend/tests/agents/test_licitor_llm_extraction.py` | Créé — 9 tests |

## Impact d=1 (appelants directs mis à jour)

- `AuctionIngestionService.ingest_session_page` — appelle `parse_listing_detail`, mis à jour pour persister l'extraction
- `execute_auction_ingestion_run` — inchangé (appelle `ingest_session_page`)

## Tests effectués

- 21/21 tests segmenteur (dont l'exemple exact de production fourni par Bilal)
- 9/9 tests service LLM extraction (OpenAI mocké)
- Fallback regex validé (LLM unavailable → code original s'active)

## Impact architectural

Le contrat `facts` dict consommé par `_apply_listing_detail` est inchangé.
Seule l'origine des données change : regex → LLM avec fallback regex.
Le scoring reste entièrement inchangé.

La table `licitor_extractions` est un journal d'audit qui permet de rejouer
le scoring ou de déboguer une extraction sans re-fetcher les pages.
