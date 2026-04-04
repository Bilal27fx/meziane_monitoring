# Refactor — Dark/Light mode toggle

**Date :** 2026-04-04  
**Statut :** Terminé

---

## Contexte

Ajout d'un bouton dark/light mode dans le header de l'UI complète.

## Périmètre

Fichiers créés :
- `frontend/lib/context/ThemeContext.tsx` — contexte + hook `useTheme`, `ThemeProvider`

Fichiers modifiés :
- `frontend/app/layout.tsx` — script inline anti-flash (lit localStorage avant hydration)
- `frontend/app/(app)/layout.tsx` — wrapping ThemeProvider, Toaster adaptatif, composant interne `AppLayoutInner`
- `frontend/components/layout/Header.tsx` — bouton toggle Sun/Moon (lucide-react)
- `frontend/app/globals.css` — overrides CSS light pour tous les tokens hexadécimaux hardcodés

## Approche technique

- `data-theme="light"` sur `<html>` via `document.documentElement.setAttribute`
- Le thème est persisté en `localStorage`
- Les overrides CSS `[data-theme="light"] .bg-\[#...\]` ciblent les classes Tailwind arbitraires hardcodées sans toucher les composants individuels
- Toaster react-hot-toast adapté via `theme` du contexte

## Impact GitNexus

- `Header` : LOW, 0 appelants directs
- `AppLayout` : LOW, 0 appelants directs
- `RootLayout` : LOW, 0 appelants directs
