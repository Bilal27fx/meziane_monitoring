'use client'

import { useEffect, useState } from 'react'
import { usePathname } from 'next/navigation'
import StatusBadge from '@/components/layout/StatusBadge'
import { useSystemHealth } from '@/lib/hooks/useSystemHealth'

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
    <header className="fixed top-0 left-12 right-0 z-10 h-14 bg-[#0d0d0d] border-b border-[#262626] flex items-center justify-between px-4">
      <span className="text-sm font-medium text-white">{getPageTitle(pathname)}</span>
      <div className="flex items-center gap-4">
        <StatusBadge status={apiStatus} label="API" />
        <StatusBadge status={celeryStatus} label="Celery" />
      </div>
      <span className="font-mono text-xs text-[#525252] tabular-nums">{clock}</span>
    </header>
  )
}
