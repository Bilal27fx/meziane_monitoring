# Refactor: locataire document download fix

## Description de la modification

- Renforcement du téléchargement navigateur dans le panneau documents générique.
- Le lien de téléchargement est maintenant injecté dans le DOM avant clic.
- La révocation de l'URL blob est différée pour laisser le navigateur démarrer l'écriture du fichier.

## Fichiers impactés

### d=1 — WILL BREAK / appelants directs

- `frontend/components/admin/panels/DocumentsPanel.tsx`
- `frontend/components/admin/tabs/LocatairesTab.tsx`
- `frontend/components/admin/tabs/BiensTab.tsx`
- `frontend/components/admin/tabs/SCITab.tsx`

### d=2 — LIKELY AFFECTED

- Téléchargement des documents depuis les panneaux admin SCI, bien et locataire
- Prévisualisation suivie d'un téléchargement dans le panneau documents

### d=3 — MAY NEED TESTING

- Comportement du téléchargement sur Safari et Chrome
- Téléchargement de PDF et d'images avec noms de fichiers variés

## Raison du changement

- Le téléchargement pouvait ne jamais démarrer côté navigateur quand l'URL blob était révoquée trop tôt ou quand le lien n'était pas attaché au DOM.
- Le symptôme remonté concernait les PDF de documents locataire.

## Tests effectués

- Relecture ciblée du flux `DocumentsPanel -> GET /api/documents/{id}/download -> blob -> anchor click`
- `npm run build` dans `frontend`

## Impact sur l'architecture

- Aucun changement de contrat API.
- Correctif purement frontend sur le déclenchement du téléchargement natif navigateur.
