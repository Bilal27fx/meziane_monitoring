# Refactor: quittance download browser fix

## Description de la modification

- Remplacement du `window.open()` par un vrai téléchargement navigateur via ancre temporaire.
- Injection de l'ancre dans le DOM avant clic.
- Révocation différée de l'URL blob pour laisser le navigateur terminer le démarrage du téléchargement.

## Fichiers impactés

### d=1 — WILL BREAK / appelants directs

- `frontend/components/admin/panels/QuittancesPanel.tsx`
- `frontend/components/admin/tabs/LocatairesTab.tsx`

### d=2 — LIKELY AFFECTED

- Téléchargement des quittances PDF depuis le panneau locataire

### d=3 — MAY NEED TESTING

- Comportement du téléchargement sur Chrome et Safari
- Nommage local du fichier téléchargé

## Raison du changement

- Le backend renvoyait bien `GET /api/quittances/{id}/pdf` en `200 OK`, mais le frontend ouvrait seulement un blob dans un nouvel onglet.
- Selon le navigateur, ce flux n'écrit pas forcément de fichier sur le poste utilisateur.

## Tests effectués

- Relecture ciblée du flux `QuittancesPanel -> GET /api/quittances/{id}/pdf -> blob -> anchor click`

## Impact sur l'architecture

- Aucun changement backend.
- Correctif purement frontend sur le déclenchement du téléchargement local.
