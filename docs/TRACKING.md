# Tracking — Meziane Monitoring

**Mis à jour :** 2026-04-04  
Source de vérité sur l'état de toutes les implémentations.
Lifecycle complet : `STANDARDS.md`

---

## En cours / Planifié

| Nom | Description | Statut | Plan |
|---|---|---|---|
| Agent Licitor V3 | Extraction LLM-first — segmenteur + appel LLM + persist JSON extraction | Planifié | [plans/2026-04-04_agent-licitor-v3-llm-extraction.md](plans/2026-04-04_agent-licitor-v3-llm-extraction.md) |

---

## Backlog

| Nom | Description | Priorité |
|---|---|---|
| Bug patrimoine 12 mois | `timedelta(days=30)` ≠ 1 mois → graphique décalé (`dashboard_service.py:235`) | Moyenne |
| Enum dupliquée | `SourceAnnonce`/`StatutOpportunite` définies 2 fois dans models + schemas | Basse |

---

## Terminé

| Nom | Description | Date | Refactor doc |
|---|---|---|---|
| Refonte scoring prix v2 | Score prix sur mise à prix réelle/m² vs marché, 5 dimensions indépendantes, deal_breakers corrigés | 2026-04-05 | [refactors/2026-04-05_scoring-prix-refonte.md](refactors/2026-04-05_scoring-prix-refonte.md) |
| Fix extraction Licitor | Date enchère + lieu visite manquants — 6 bugs corrigés | 2026-04-04 | [refactors/2026-04-04_licitor-extraction-fix.md](refactors/2026-04-04_licitor-extraction-fix.md) |
| Agent Licitor V2 | URLs backend + scoring LLM post-ingestion | 2026-04-03 | [refactors/2026-04-03_agent-licitor-v2.md](refactors/2026-04-03_agent-licitor-v2.md) |
| Restructuration documentation | Nettoyage doc, nouveau lifecycle STANDARDS.md | 2026-04-03 | [refactors/2026-04-03_restructuration-documentation.md](refactors/2026-04-03_restructuration-documentation.md) |
| RFC-008 | Sécurité Auth + Performance suite | 2026-03-24 | [archive/RFC/RFC-008](archive/RFC/RFC-008_security-auth-perf/README.md) |
| RFC-007 | Scalabilité & Performance Backend | 2026-03-24 | [archive/RFC/RFC-007](archive/RFC/RFC-007_scalability-performance/README.md) |
| RFC-006 | Suppression totale mock data + branchement API | 2026-03-24 | — |
| RFC-005 | Suppression mock data fallback silencieux | 2026-03-24 | [archive/RFC/RFC-005](archive/RFC/RFC-005_mock-data-fallback/README.md) |
| RFC-004 | Boutons QuittancesPanel connectés API | 2026-03-24 | [archive/RFC/RFC-004](archive/RFC/RFC-004_quittances-panel-api/README.md) |
| RFC-003 | Upload documents locataire | 2026-03-24 | [archive/RFC/RFC-003](archive/RFC/RFC-003_upload-documents-locataire/README.md) |
| RFC-002 | Routes backend quittances | 2026-03-24 | [archive/RFC/RFC-002](archive/RFC/RFC-002_quittance-routes-backend/README.md) |
| RFC-001 | Fix endpoints validate/reject | 2026-03-24 | [archive/RFC/RFC-001](archive/RFC/RFC-001_fix-endpoints-validate-reject/README.md) |
| Licitor quick launch + HTTP fetch | Endpoint lancement rapide + fetch HTTP pages audience | 2026-03-26 | [refactors/2026-03-26_licitor-quick-launch-and-http-fetch.md](refactors/2026-03-26_licitor-quick-launch-and-http-fetch.md) |
| Auction agents foundation backend | Modèles, runs, events, tâches Celery | 2026-03-26 | [refactors/2026-03-26_auction-agents-foundation-backend.md](refactors/2026-03-26_auction-agents-foundation-backend.md) |
| Licitor ingestion run foundation | Adapter + ingestion service + tests parsing | 2026-03-26 | [refactors/2026-03-26_licitor-ingestion-run-foundation.md](refactors/2026-03-26_licitor-ingestion-run-foundation.md) |
| Locataire payments tracking | Suivi paiements locataires | 2026-03-25 | [refactors/2026-03-25_locataire-payments-tracking-foundation.md](refactors/2026-03-25_locataire-payments-tracking-foundation.md) |
| Quittance PDF natif | Génération PDF quittances | 2026-03-25 | [refactors/2026-03-25_quittance-pdf-native-generator.md](refactors/2026-03-25_quittance-pdf-native-generator.md) |
| Documents folders | Bibliothèque documents avec dossiers | 2026-03-25 | [refactors/2026-03-25_documents-folder-library-foundation.md](refactors/2026-03-25_documents-folder-library-foundation.md) |
