# Instructions Claude - Meziane Monitoring

**Version 3.0 - 25 mars 2026**

Ce document définit le cadre de travail pour toute modification du projet. Il ne remplace pas le code ni les autres docs: il indique quoi lire, dans quel ordre, et quelles règles respecter avant d'éditer quoi que ce soit.

## 1. Documents à lire en premier

Lire ces documents avant toute tâche non triviale:

1. `docs/architecture/PROFIL_ET_OBJECTIFS.md`
2. `docs/architecture/ARCHITECTURE_SYSTEME.md`
3. `docs/architecture/FRONTEND_ARCHITECTURE.md`
4. `docs/TRACKING.md`

Rôle de chaque document:
- `PROFIL_ET_OBJECTIFS.md`: contexte business, objectifs, contraintes métier.
- `ARCHITECTURE_SYSTEME.md`: architecture cible backend, flux de données, domaines.
- `FRONTEND_ARCHITECTURE.md`: vision UI, structure des pages, conventions frontend.
- `TRACKING.md`: état vivant — backlog, en cours, terminé. Contient les liens vers les plans (`docs/plans/`) et les refactor docs (`docs/refactors/`).

Règle lifecycle documentaire: voir `docs/STANDARDS.md`.

Règles d'interprétation:
- Les docs d'architecture donnent la direction.
- Le code en place décrit l'état réel.
- Si doc et code divergent, il faut le signaler explicitement avant de modifier l'architecture.
- Ne jamais inventer une fonctionnalité ou changer une direction produit sans validation explicite de Bilal.

## 2. GitNexus: règle absolue avant modification de code

Avant toute modification de code, il faut analyser l'impact.

Workflow obligatoire:
1. Vérifier que l'index GitNexus existe et n'est pas vide.
2. Vérifier sa fraîcheur.
3. Identifier les symboles touchés et leurs dépendances.
4. Evaluer le risque avant édition.

Vérification minimale:

```bash
cat .gitnexus/meta.json
```

Points à vérifier:
- `stats.nodes > 0`
- `indexedAt` récent
- `stats.embeddings` conservé si le projet en utilise déjà

Si l'index est absent, vide ou stale, utiliser l'image Docker dédiée.
Ne pas utiliser la méthode locale `npx gitnexus analyze` dans cet environnement.

```bash
docker run --rm -v "/Users/bilalmeziane/Desktop/Meziane_Monitoring:/workspace" -w /workspace gitnexus:latest
```

Si l'environnement local GitNexus est bloqué, utiliser l'image Docker dédiée:

```bash
docker run --rm -v "/Users/bilalmeziane/Desktop/Meziane_Monitoring:/workspace" -w /workspace gitnexus:latest
```

Règles d'analyse d'impact:
- Ne jamais modifier une fonction, classe ou méthode sans analyse préalable.
- Ne jamais ignorer un risque HIGH ou CRITICAL.
- Ne jamais faire un renommage par simple recherche/remplacement.
- Toujours identifier les dépendances directes `d=1` avant d'éditer.

Fallback si les outils GitNexus sont indisponibles:
- lire `.gitnexus/meta.json`
- utiliser `rg` pour trouver définitions, imports et appelants
- tracer manuellement les dépendances les plus proches

Exemples utiles:

```bash
rg "def nom_fonction|class NomClasse" backend frontend
rg "nom_fonction\\(" backend frontend
rg "from app\\.module import NomClasse|import .*NomClasse" backend frontend
```

## 3. Obligations après modification de code

Après toute modification de code:

1. Créer `docs/refactors/YYYY-MM-DD_nom-court.md` (format dans `docs/STANDARDS.md`)
2. Mettre à jour `docs/TRACKING.md` : statut `Terminé` + lien vers le refactor doc
3. Relancer `npx gitnexus analyze`

Sans refactor doc + mise à jour TRACKING.md, la modification est incomplète.

## 4. Règles de développement

### 4.1 Règles produit

- Bilal décide de la direction produit.
- Ne pas ajouter de fonctionnalité non demandée.
- Ne pas modifier l'architecture cible sans l'expliciter.
- Si une demande contredit la doc existante, le dire clairement avant d'exécuter.

### 4.2 Style de code

- Code concis.
- Nommage explicite.
- Pas de code mort.
- Pas de sur-engineering.
- Refactoriser quand cela réduit vraiment le risque ou la complexité.

### 4.3 Documentation des fichiers

Chaque fichier métier important doit commencer par un court en-tête descriptif:

```python
"""
[nom_fichier] - [responsabilite en une ligne]

Description:
[2-3 phrases max]

Dependances:
- [...]

Utilise par:
- [...]
"""
```

### 4.4 Commentaires et fonctions

- Préférer du code lisible à des commentaires verbeux.
- Si un commentaire de fonction est nécessaire, il doit tenir sur une ligne.
- Décrire ce que fait la fonction, pas son implémentation détaillée.

Exemple:

```python
def calculate_cashflow(transactions: list[Transaction]) -> float:  # Calcule le cashflow net
    ...
```

### 4.5 Nommage

- variables: `snake_case`
- fonctions: `snake_case`
- classes: `PascalCase`
- constantes: `UPPER_SNAKE_CASE`
- fichiers Python: `snake_case.py`

### 4.6 Gestion d'erreurs

- Utiliser `try/except` là où il y a un vrai risque IO, DB, réseau ou parsing.
- Logger les erreurs utiles.
- Eviter les `except: pass` silencieux.
- Si un fallback silencieux est temporairement nécessaire, le justifier par un commentaire court.

### 4.7 Tests

- Ajouter des tests sur la logique métier critique dès que le changement le justifie.
- Nommer les tests de façon explicite.
- Utiliser une structure claire: Arrange / Act / Assert.

## 5. Structure réelle du repository

Vue d'ensemble actuelle:

```text
Meziane_Monitoring/
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── docker-compose.yml
├── Dockerfile.gitnexus
├── backend/
│   ├── README.md
│   ├── alembic/
│   ├── app/
│   │   ├── api/
│   │   ├── agents/
│   │   ├── connectors/
│   │   ├── models/
│   │   ├── plugins/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── tasks/
│   │   └── utils/
│   └── requirements.txt
├── frontend/
│   ├── README.md
│   ├── AGENTS.md
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── public/
└── docs/
    ├── README.md
    ├── PLAN.md
    ├── TRACKING.md
    ├── architecture/
    ├── history/
    └── refactors/
```

Remarques:
- Les docs historiques sont dans `docs/history/`.
- Les docs d'architecture actives sont dans `docs/architecture/`.
- Les refactors et correctifs livrés sont dans `docs/refactors/`.

## 6. Workflow recommandé

### Avant de coder

1. Lire les docs de contexte utiles.
2. Vérifier GitNexus et l'impact.
3. Comparer demande, code actuel et architecture cible.
4. Signaler tout écart important avant édition.

### Pendant le travail

1. Respecter les conventions du repo.
2. Limiter le périmètre de changement.
3. Garder la cohérence avec les appelants identifiés.
4. Mettre à jour la doc si la modification change un comportement important.

### Après le travail

1. Relire les changements.
2. Tester ce qui peut l'être.
3. Documenter dans `docs/refactors/` si du code a changé.
4. Relancer GitNexus si nécessaire.

## 7. Points d'attention spécifiques au projet

- Le frontend et le backend évoluent vite: vérifier que les chemins et versions documentés sont encore valides.
- `docs/history/` contient des archives utiles mais ne doit pas être traité comme la source de vérité active.
- `frontend/AGENTS.md` rappelle que la version de Next.js utilisée peut diverger de ce qu'un assistant connaît par défaut.
- Les docs doivent rester alignées avec l'état réel du repo, pas seulement avec l'intention initiale.

## 8. Interdictions absolues

- Ne jamais coder sans analyse d'impact préalable.
- Ne jamais ignorer un risque GitNexus élevé.
- Ne jamais renommer par recherche/remplacement brut.
- Ne jamais oublier le document de refactor après modification de code.
- Ne jamais contredire la direction produit sans l'indiquer clairement.
- Ne jamais laisser une doc d'entrée pointer vers des chemins obsolètes.

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **meziane_monitoring** (2498 symbols, 5530 relationships, 130 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## When Debugging

1. `gitnexus_query({query: "<error or symptom>"})` — find execution flows related to the issue
2. `gitnexus_context({name: "<suspect function>"})` — see all callers, callees, and process participation
3. `READ gitnexus://repo/meziane_monitoring/process/{processName}` — trace the full execution flow step by step
4. For regressions: `gitnexus_detect_changes({scope: "compare", base_ref: "main"})` — see what your branch changed

## When Refactoring

- **Renaming**: MUST use `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` first. Review the preview — graph edits are safe, text_search edits need manual review. Then run with `dry_run: false`.
- **Extracting/Splitting**: MUST run `gitnexus_context({name: "target"})` to see all incoming/outgoing refs, then `gitnexus_impact({target: "target", direction: "upstream"})` to find all external callers before moving code.
- After any refactor: run `gitnexus_detect_changes({scope: "all"})` to verify only expected files changed.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Tools Quick Reference

| Tool | When to use | Command |
|------|-------------|---------|
| `query` | Find code by concept | `gitnexus_query({query: "auth validation"})` |
| `context` | 360-degree view of one symbol | `gitnexus_context({name: "validateUser"})` |
| `impact` | Blast radius before editing | `gitnexus_impact({target: "X", direction: "upstream"})` |
| `detect_changes` | Pre-commit scope check | `gitnexus_detect_changes({scope: "staged"})` |
| `rename` | Safe multi-file rename | `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` |
| `cypher` | Custom graph queries | `gitnexus_cypher({query: "MATCH ..."})` |

## Impact Risk Levels

| Depth | Meaning | Action |
|-------|---------|--------|
| d=1 | WILL BREAK — direct callers/importers | MUST update these |
| d=2 | LIKELY AFFECTED — indirect deps | Should test |
| d=3 | MAY NEED TESTING — transitive | Test if critical path |

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/meziane_monitoring/context` | Codebase overview, check index freshness |
| `gitnexus://repo/meziane_monitoring/clusters` | All functional areas |
| `gitnexus://repo/meziane_monitoring/processes` | All execution flows |
| `gitnexus://repo/meziane_monitoring/process/{name}` | Step-by-step execution trace |

## Self-Check Before Finishing

Before completing any code modification task, verify:
1. `gitnexus_impact` was run for all modified symbols
2. No HIGH/CRITICAL risk warnings were ignored
3. `gitnexus_detect_changes()` confirms changes match expected scope
4. All d=1 (WILL BREAK) dependents were updated

## Keeping the Index Fresh

After committing code changes, the GitNexus index becomes stale. Re-run analyze to update it:

```bash
npx gitnexus analyze
```

If the index previously included embeddings, preserve them by adding `--embeddings`:

```bash
npx gitnexus analyze --embeddings
```

To check whether embeddings exist, inspect `.gitnexus/meta.json` — the `stats.embeddings` field shows the count (0 means no embeddings). **Running analyze without `--embeddings` will delete any previously generated embeddings.**

> Claude Code users: A PostToolUse hook handles this automatically after `git commit` and `git merge`.

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
