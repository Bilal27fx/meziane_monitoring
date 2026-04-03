# 2026-03-25 — Panneau documents réduit à deux actions

## Contexte

Le panneau documents exposait en permanence des champs de saisie, ce qui alourdissait le flux principal. Le besoin produit était plus simple: n'afficher que deux actions claires, `Upload document` et `Créer un dossier`, puis demander les informations utiles seulement après clic.

## Changements effectués

- remplacement du bloc de saisie toujours visible par deux CTA principaux
- `Créer un dossier` ouvre un mini-flux avec saisie du nom puis enregistrement
- `Upload document` ouvre un mini-flux avec:
  - choix du dossier cible ou racine
  - nom optionnel du document
  - sélection du fichier
- conservation de la navigation dans les dossiers et de la prévisualisation existante

## Fichier impacté

- `frontend/components/admin/panels/DocumentsPanel.tsx`

## Impact

- d=1 frontend: changement d'interaction sur les panneaux documents SCI, bien et locataire
- d=2 produit/UI: flux plus direct et plus proche de l'usage demandé

## Tests effectués

- relecture du composant et contrôle de portée par recherche d'appelants
- validation manuelle du blast radius sur les trois tabs admin qui utilisent `DocumentsPanel`

## Limite actuelle

Le choix du dossier se fait sur la racine, le dossier courant et les dossiers visibles au niveau courant. Une API d'arborescence complète pourra être ajoutée plus tard si l'on veut sélectionner n'importe quel sous-dossier sans y naviguer d'abord.
