# Documentation - Meziane Monitoring

Ce dossier centralise la documentation active, l'historique et les refactors du projet.

## Ordre de lecture recommandé

Si tu découvres le repo:

1. `../CLAUDE.md`
2. `architecture/PROFIL_ET_OBJECTIFS.md`
3. `architecture/ARCHITECTURE_SYSTEME.md`
4. `architecture/FRONTEND_ARCHITECTURE.md`
5. `PLAN.md`
6. `TRACKING.md`

## Structure du dossier

### `architecture/`

Documentation active sur la cible fonctionnelle et technique:
- `PROFIL_ET_OBJECTIFS.md`: contexte business et objectifs.
- `ARCHITECTURE_SYSTEME.md`: architecture backend et flux principaux.
- `FRONTEND_ARCHITECTURE.md`: vision UI, structure et conventions front.
- `DASHBOARD_LAYOUT_PLAN.md`: plan détaillé du dashboard.
- `SCALABILITY_AUDIT.md`: audit performance et scalabilité.

### `history/`

Archives de phases précédentes:
- plans anciens
- progression backend
- progression frontend

Ces fichiers sont utiles pour le contexte, mais ne doivent pas être considérés comme la source de vérité active par défaut.

### `refactors/`

Historique des modifications importantes et des RFC:
- dossiers `RFC-*` pour les RFC formalisées
- fichiers datés `YYYY-MM-DD_*` pour les refactors et correctifs livrés

Chaque modification de code importante devrait laisser une trace ici.

## Quelle doc lire selon le besoin

Pour comprendre le produit:
- `architecture/PROFIL_ET_OBJECTIFS.md`

Pour comprendre l'architecture:
- `architecture/ARCHITECTURE_SYSTEME.md`
- `architecture/FRONTEND_ARCHITECTURE.md`

Pour connaître l'état du chantier:
- `PLAN.md`
- `TRACKING.md`

Pour comprendre l'historique d'une évolution:
- `refactors/`

Pour retrouver d'anciens plans ou arbitrages:
- `history/`

## Règles de maintenance documentaire

- Garder les chemins et noms de fichiers alignés avec le repo réel.
- Eviter les statuts contradictoires entre `PLAN.md`, `TRACKING.md` et les docs de refactor.
- Ne pas laisser un README d'entrée pointer vers des fichiers inexistants.
- Quand une modification change le comportement ou le workflow, mettre à jour la doc correspondante dans le même mouvement.
