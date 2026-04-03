# Standards documentation — Meziane Monitoring

**Référence centrale.** Ce fichier définit le lifecycle documentaire du projet.
Toute modification de code ou de direction produit doit suivre ces règles.

---

## Structure des dossiers

```
docs/
├── STANDARDS.md          ← ce fichier (règles)
├── TRACKING.md           ← état vivant de toutes les implémentations
├── architecture/         ← vérités durables (ne changent que si l'architecture change)
├── plans/                ← plans validés, en attente d'implémentation
├── refactors/            ← journal des livraisons (une entrée par merge)
└── archive/              ← tout l'historique, jamais supprimé
```

---

## Lifecycle d'une implémentation

```
IDÉE → PLAN → DEV → LIVRAISON
```

### 1. Idée
- Ajouter une ligne dans `TRACKING.md` section **Backlog**
- Format : `| nom court | description une ligne | - |`
- Aucun fichier créé

### 2. Plan
- Créer `plans/YYYY-MM-DD_nom-court.md`
- Mettre à jour `TRACKING.md` : statut `Planifié`, lien vers le plan
- Le plan doit contenir : contexte, périmètre, fichiers touchés, ordre d'exécution, tests attendus
- **Ne pas coder avant que le plan soit validé**

### 3. Dev (en cours)
- Mettre à jour `TRACKING.md` : statut `En cours`
- Pas de nouveau fichier doc pendant le dev

### 4. Livraison (après merge)
- Créer `refactors/YYYY-MM-DD_nom-court.md` (voir format ci-dessous)
- Mettre à jour `TRACKING.md` : statut `Terminé`, lien vers le refactor doc
- Déplacer le plan dans `archive/plans/` (ou le laisser dans `plans/` avec mention "Livré")
- Relancer `npx gitnexus analyze`

---

## Format d'un plan (`plans/`)

```markdown
# Plan — [Nom]
**Date :** YYYY-MM-DD
**Statut :** À valider | Validé | Livré

## Contexte
## Ce qui existe déjà (ne pas toucher)
## Périmètre — fichiers modifiés / créés
## Étapes (numérotées, avec ordre d'exécution)
## Ce qu'on ne fait PAS
## Tests attendus
```

---

## Format d'un refactor doc (`refactors/`)

```markdown
# YYYY-MM-DD — [Nom]
**Commit(s) :** abc1234
**Plan source :** plans/YYYY-MM-DD_nom.md (si applicable)

## Changements effectués
## Fichiers impactés
## Impact d=1 (appelants directs mis à jour)
## Tests effectués
## Impact architectural (si pertinent)
```

---

## Règles de nommage

| Dossier | Format fichier | Exemple |
|---|---|---|
| `plans/` | `YYYY-MM-DD_nom-kebab-case.md` | `2026-04-03_agent-licitor-v2.md` |
| `refactors/` | `YYYY-MM-DD_nom-kebab-case.md` | `2026-04-03_licitor-scoring-llm.md` |
| `archive/` | conserver le nom d'origine | — |

---

## Ce qui va dans `architecture/`

Uniquement les documents qui décrivent **l'état cible durable** du système :
- `PROFIL_ET_OBJECTIFS.md` — contexte business et contraintes
- `ARCHITECTURE_SYSTEME.md` — flux backend, domaines, services
- `FRONTEND_ARCHITECTURE.md` — conventions UI, structure pages

**Ne pas mettre dans `architecture/` :** plans one-shot, audits ponctuels, drafts.

---

## Ce qui va dans `archive/`

Tout ce qui n'est plus actif mais doit être conservé :
- RFC terminées (`archive/RFC/`)
- Anciens plans de progression (`archive/history/`)
- Drafts d'architecture dépassés (`archive/architecture-drafts/`)

**Ne jamais supprimer** — archiver uniquement.

---

## Règle GitNexus

Avant tout dev :
1. Vérifier fraîcheur index : `cat .gitnexus/meta.json`
2. Analyser l'impact : `gitnexus_impact({target: "symbolName", direction: "upstream"})`
3. Après livraison : relancer `npx gitnexus analyze`
