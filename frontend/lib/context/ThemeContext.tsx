'use client'

import { createContext, useContext, useEffect, useState } from 'react'

type Theme = 'dark' | 'light'

interface ThemeContextValue {
  theme: Theme
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextValue>({
  theme: 'dark',
  toggleTheme: () => {},
})

// Tailwind v4 + Lightning CSS génère des sélecteurs avec # échappé : .bg-\[\#111111\]
// En JS template literal : \\[\\#111111\\] → \[\#111111\] dans le CSS final
const LIGHT_THEME_CSS = `
  /* ── Gradients sombres → fond clair (sélecteur attribut, pas de classe) ── */
  [data-theme="light"] [class*="linear-gradient"] { background: #f2f2f2 !important; }

  /* ── Backgrounds sombres → clairs ── */
  [data-theme="light"] .bg-\\[\\#0a0a0a\\] { background-color: #ffffff !important; }
  [data-theme="light"] .bg-\\[\\#0d0d0d\\] { background-color: #fafafa !important; }
  [data-theme="light"] .bg-\\[\\#111\\]     { background-color: #f2f2f2 !important; }
  [data-theme="light"] .bg-\\[\\#121212\\]  { background-color: #f4f4f4 !important; }
  [data-theme="light"] .bg-\\[\\#111111\\] { background-color: #f2f2f2 !important; }
  [data-theme="light"] .bg-\\[\\#141414\\] { background-color: #ededed !important; }
  [data-theme="light"] .bg-\\[\\#161616\\] { background-color: #ebebeb !important; }
  [data-theme="light"] .bg-\\[\\#171717\\] { background-color: #ebebeb !important; }
  [data-theme="light"] .bg-\\[\\#1a1a1a\\] { background-color: #e8e8e8 !important; }
  [data-theme="light"] .bg-\\[\\#1f1f1f\\] { background-color: #e4e4e4 !important; }
  [data-theme="light"] .bg-\\[\\#222222\\] { background-color: #e2e2e2 !important; }
  [data-theme="light"] .bg-\\[\\#262626\\] { background-color: #dedede !important; }
  [data-theme="light"] .bg-\\[\\#2a2a2a\\] { background-color: #dadada !important; }
  [data-theme="light"] .bg-\\[\\#333333\\] { background-color: #d0d0d0 !important; }
  [data-theme="light"] .bg-\\[\\#3f3f3f\\] { background-color: #c8c8c8 !important; }
  [data-theme="light"] .bg-\\[\\#404040\\] { background-color: #c4c4c4 !important; }
  [data-theme="light"] .bg-\\[\\#525252\\] { background-color: #b8b8b8 !important; }
  [data-theme="light"] .bg-\\[\\#737373\\] { background-color: #a0a0a0 !important; }
  [data-theme="light"] .bg-\\[\\#a3a3a3\\] { background-color: #888888 !important; }
  [data-theme="light"] .bg-\\[\\#e5e5e5\\] { background-color: #cccccc !important; }

  /* ── Backgrounds bleutés sombres → clairs ── */
  [data-theme="light"] .bg-\\[\\#0b1220\\] { background-color: #dbeafe !important; }
  [data-theme="light"] .bg-\\[\\#0d1520\\] { background-color: #dbeafe !important; }
  [data-theme="light"] .bg-\\[\\#101722\\] { background-color: #eff6ff !important; }

  /* ── Backgrounds verdâtres sombres → clairs ── */
  [data-theme="light"] .bg-\\[\\#0d1711\\] { background-color: #f0fdf4 !important; }
  [data-theme="light"] .bg-\\[\\#0f1a12\\] { background-color: #f0fdf4 !important; }
  [data-theme="light"] .bg-\\[\\#12311f\\] { background-color: #dcfce7 !important; }
  [data-theme="light"] .bg-\\[\\#14532d\\] { background-color: #bbf7d0 !important; }
  [data-theme="light"] .bg-\\[\\#16a34a\\] { background-color: #22c55e !important; }
  [data-theme="light"] .bg-\\[\\#17462c\\] { background-color: #d1fae5 !important; }
  [data-theme="light"] .bg-\\[\\#1f3a2a\\] { background-color: #d1fae5 !important; }

  /* ── Textes clairs → sombres ── */
  [data-theme="light"] .text-white          { color: #111111 !important; }
  [data-theme="light"] .text-\\[\\#d4d4d4\\] { color: #444444 !important; }
  [data-theme="light"] .text-\\[\\#a3a3a3\\] { color: #555555 !important; }
  [data-theme="light"] .text-\\[\\#737373\\] { color: #666666 !important; }
  [data-theme="light"] .text-\\[\\#525252\\] { color: #888888 !important; }
  [data-theme="light"] .text-\\[\\#404040\\] { color: #777777 !important; }
  [data-theme="light"] .text-\\[\\#262626\\] { color: #444444 !important; }
  [data-theme="light"] .text-\\[\\#8f8f8f\\] { color: #666666 !important; }
  [data-theme="light"] .text-\\[\\#8fb3a0\\] { color: #1a6648 !important; }
  [data-theme="light"] .text-\\[\\#c7d2cc\\] { color: #3d6055 !important; }
  [data-theme="light"] .text-\\[\\#9ca3af\\] { color: #6b7280 !important; }
  [data-theme="light"] .text-\\[\\#d1d5db\\] { color: #4b5563 !important; }
  [data-theme="light"] .text-\\[\\#cbd5e1\\] { color: #475569 !important; }
  [data-theme="light"] .text-\\[\\#6b7280\\] { color: #374151 !important; }
  [data-theme="light"] .text-\\[\\#6ee7b7\\] { color: #059669 !important; }
  [data-theme="light"] .text-\\[\\#86efac\\] { color: #16a34a !important; }
  [data-theme="light"] .text-\\[\\#bbf7d0\\] { color: #15803d !important; }
  [data-theme="light"] .text-\\[\\#d1fae5\\] { color: #166534 !important; }
  [data-theme="light"] .text-\\[\\#93c5fd\\] { color: #2563eb !important; }
  [data-theme="light"] .text-\\[\\#dbeafe\\] { color: #1d4ed8 !important; }
  [data-theme="light"] .text-\\[\\#fca5a5\\] { color: #dc2626 !important; }

  /* ── Borders sombres → claires ── */
  [data-theme="light"] .border-\\[\\#1f1f1f\\] { border-color: #e2e2e2 !important; }
  [data-theme="light"] .border-\\[\\#1f3a2b\\] { border-color: #bbf7d0 !important; }
  [data-theme="light"] .border-\\[\\#1e3a5f\\] { border-color: #bfdbfe !important; }
  [data-theme="light"] .border-\\[\\#24553a\\] { border-color: #86efac !important; }
  [data-theme="light"] .border-\\[\\#262626\\] { border-color: #d8d8d8 !important; }
  [data-theme="light"] .border-\\[\\#2a2a2a\\] { border-color: #d4d4d4 !important; }
  [data-theme="light"] .border-\\[\\#303030\\] { border-color: #cccccc !important; }
  [data-theme="light"] .border-\\[\\#404040\\] { border-color: #c0c0c0 !important; }

  /* ── Divide ── */
  [data-theme="light"] .divide-\\[\\#262626\\] > :not([hidden]) ~ :not([hidden]) {
    border-color: #d8d8d8 !important;
  }

  /* ── Placeholder ── */
  [data-theme="light"] .placeholder-\\[\\#525252\\]::placeholder { color: #999999 !important; }

  /* ── Focus ── */
  [data-theme="light"] .focus\\:border-\\[\\#404040\\]:focus { border-color: #bbbbbb !important; }

  /* ── Hover backgrounds ── */
  [data-theme="light"] .hover\\:bg-\\[\\#0d0d0d\\]:hover  { background-color: #f0f0f0 !important; }
  [data-theme="light"] .hover\\:bg-\\[\\#111111\\]:hover  { background-color: #ebebeb !important; }
  [data-theme="light"] .hover\\:bg-\\[\\#1a1a1a\\]:hover  { background-color: #e4e4e4 !important; }
  [data-theme="light"] .hover\\:bg-\\[\\#1f1f1f\\]:hover  { background-color: #e0e0e0 !important; }
  [data-theme="light"] .hover\\:bg-\\[\\#262626\\]:hover  { background-color: #dadada !important; }
  [data-theme="light"] .hover\\:bg-\\[\\#404040\\]:hover  { background-color: #cccccc !important; }
  [data-theme="light"] .hover\\:bg-\\[\\#e5e5e5\\]:hover  { background-color: #cccccc !important; }
  [data-theme="light"] .hover\\:bg-\\[\\#17462c\\]:hover  { background-color: #bbf7d0 !important; }

  /* ── Hover textes ── */
  [data-theme="light"] .hover\\:text-white:hover { color: #111111 !important; }

  /* ── Hover borders ── */
  [data-theme="light"] .hover\\:border-\\[\\#404040\\]:hover { border-color: #bbbbbb !important; }

  /* ── Input fields ── */
  [data-theme="light"] input, [data-theme="light"] textarea, [data-theme="light"] select {
    background-color: #fafafa !important;
    color: #111111 !important;
    border-color: #d8d8d8 !important;
  }
`

let styleEl: HTMLStyleElement | null = null

function applyTheme(theme: Theme) {
  document.documentElement.setAttribute('data-theme', theme)

  if (theme === 'light') {
    if (!styleEl) {
      styleEl = document.createElement('style')
      styleEl.id = '__theme-light-overrides'
      document.head.appendChild(styleEl)
    }
    styleEl.textContent = LIGHT_THEME_CSS
  } else {
    styleEl?.remove()
    styleEl = null
  }
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>('dark')

  useEffect(() => {
    const saved = localStorage.getItem('theme') as Theme | null
    const resolved: Theme = saved === 'light' ? 'light' : 'dark'
    setTheme(resolved)
    applyTheme(resolved)
  }, [])

  const toggleTheme = () => {
    const next: Theme = theme === 'dark' ? 'light' : 'dark'
    setTheme(next)
    localStorage.setItem('theme', next)
    applyTheme(next)
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => useContext(ThemeContext)
