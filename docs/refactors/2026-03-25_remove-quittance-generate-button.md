# Refactor: remove quittance generate button

## Description de la modification

- Suppression du bouton `Générer quittance` du panneau quittances locataire.
- Suppression du hook frontend `useGenerateQuittance` devenu inutilisé.

## Fichiers impactés

### d=1 — WILL BREAK / appelants directs

- `frontend/components/admin/panels/QuittancesPanel.tsx`
- `frontend/lib/hooks/useAdmin.ts`

### d=2 — LIKELY AFFECTED

- Panneau quittances depuis l’onglet locataires

### d=3 — MAY NEED TESTING

- Parcours de consultation/téléchargement des quittances
- Marquage `payée` depuis le panneau

## Raison du changement

- Le besoin utilisateur est de ne plus exposer l’action de génération de quittance dans l’interface.

## Tests effectués

- Vérification de l’absence de références frontend restantes à `useGenerateQuittance`
- Relecture du panneau quittances après suppression du footer d’action

## Impact sur l'architecture

- Aucun changement backend.
- Le contrat API reste inchangé ; seule l’action UI est retirée.
