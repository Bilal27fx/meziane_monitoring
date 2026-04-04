'use client'

import { useEffect, useState } from 'react'
import { usePathname } from 'next/navigation'
import { Sun, Moon } from 'lucide-react'
import StatusBadge from '@/components/layout/StatusBadge'
import { useSystemHealth } from '@/lib/hooks/useSystemHealth'
import { useTheme } from '@/lib/context/ThemeContext'

const PAGE_TITLES: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/agent': 'Agent IA',
  '/admin': 'Administration',
}

function getPageTitle(pathname: string): string {
  for (const [path, title] of Object.entries(PAGE_TITLES)) {
    if (pathname === path || pathname.startsWith(path + '/')) return title
  }
  return 'Meziane Monitoring'
}

export default function Header() {
  const pathname = usePathname()
  const [clock, setClock] = useState('')
  const { data, isLoading, isError } = useSystemHealth()
  const { theme, toggleTheme } = useTheme()

  useEffect(() => {
    const update = () => {
      const now = new Date()
      const time = now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      const date = now.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' })
      setClock(`${time} · ${date}`)
    }
    update()
    const id = setInterval(update, 1000)
    return () => clearInterval(id)
  }, [])

  const apiStatus = isError ? 'offline' : isLoading ? 'unknown' : data?.api === 'online' ? 'online' : 'offline'
  const celeryStatus = isError ? 'unknown' : isLoading ? 'unknown' : data?.celery === 'online' ? 'online' : 'offline'

  return (
    <header
      className="fixed top-0 left-12 right-0 z-10 h-14 flex items-center justify-between px-4"
      style={{
        backgroundColor: 'var(--t-bg-overlay)',
        borderBottom: '1px solid var(--t-border)',
      }}
    >
      <span className="text-sm font-medium" style={{ color: 'var(--t-text)' }}>
        {getPageTitle(pathname)}
      </span>
      <div className="flex items-center gap-4">
        <StatusBadge status={apiStatus} label="API" />
        <StatusBadge status={celeryStatus} label="Celery" />
        <button
          onClick={toggleTheme}
          title={theme === 'dark' ? 'Passer en mode clair' : 'Passer en mode sombre'}
          className="w-7 h-7 flex items-center justify-center rounded-md transition-colors"
          style={{
            color: 'var(--t-text-faint)',
            backgroundColor: 'transparent',
          }}
          onMouseEnter={e => {
            (e.currentTarget as HTMLButtonElement).style.backgroundColor = 'var(--t-bg-hover)'
            ;(e.currentTarget as HTMLButtonElement).style.color = 'var(--t-text)'
          }}
          onMouseLeave={e => {
            (e.currentTarget as HTMLButtonElement).style.backgroundColor = 'transparent'
            ;(e.currentTarget as HTMLButtonElement).style.color = 'var(--t-text-faint)'
          }}
        >
          {theme === 'dark' ? <Sun className="h-3.5 w-3.5" /> : <Moon className="h-3.5 w-3.5" />}
        </button>
      </div>
      <span className="font-mono text-xs tabular-nums" style={{ color: 'var(--t-text-faint)' }}>
        {clock}
      </span>
    </header>
  )
}
