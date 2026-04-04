'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState, useRef, useEffect } from 'react'
import { LayoutGrid, Zap, Settings2, LogOut } from 'lucide-react'
import { cn } from '@/lib/utils/cn'
import { useAuth } from '@/lib/hooks/useAuth'
import { tokenStore } from '@/lib/api/client'

const NAV_ITEMS = [
  { href: '/dashboard', icon: LayoutGrid, label: 'Dashboard' },
  { href: '/agent', icon: Zap, label: 'Agent IA' },
  { href: '/admin', icon: Settings2, label: 'Administration', adminOnly: true },
]

export default function Sidebar() {
  const pathname = usePathname()
  const { logout } = useAuth()
  const role = tokenStore.getRole()
  const [menuOpen, setMenuOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false)
      }
    }
    if (menuOpen) document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [menuOpen])

  return (
    <aside
      className="fixed left-0 top-0 h-screen w-12 z-20 flex flex-col items-center"
      style={{
        backgroundColor: 'var(--t-bg-overlay)',
        borderRight: '1px solid var(--t-border)',
      }}
    >
      {/* Logo → Dashboard */}
      <Link
        href="/dashboard"
        className="h-14 flex items-center justify-center w-full transition-colors"
        style={{ borderBottom: '1px solid var(--t-border)' }}
        title="Dashboard"
        onMouseEnter={e => (e.currentTarget as HTMLAnchorElement).style.backgroundColor = 'var(--t-bg-hover)'}
        onMouseLeave={e => (e.currentTarget as HTMLAnchorElement).style.backgroundColor = 'transparent'}
      >
        <span className="text-sm font-bold" style={{ color: 'var(--t-text)' }}>M</span>
      </Link>

      {/* Nav */}
      <nav className="flex flex-col items-center gap-1 pt-2 flex-1">
        {NAV_ITEMS.filter(item => !item.adminOnly || role === 'admin').map(({ href, icon: Icon, label }) => {
          const isActive = pathname === href || pathname.startsWith(href + '/')
          return (
            <Link
              key={href}
              href={href}
              title={label}
              className="w-10 h-10 mx-auto rounded-md flex items-center justify-center transition-colors"
              style={{
                backgroundColor: isActive ? 'var(--t-bg-active)' : 'transparent',
                color: isActive ? 'var(--t-text)' : 'var(--t-text-faint)',
              }}
              onMouseEnter={e => {
                if (!isActive) {
                  (e.currentTarget as HTMLAnchorElement).style.backgroundColor = 'var(--t-bg-hover)'
                  ;(e.currentTarget as HTMLAnchorElement).style.color = 'var(--t-text)'
                }
              }}
              onMouseLeave={e => {
                if (!isActive) {
                  (e.currentTarget as HTMLAnchorElement).style.backgroundColor = 'transparent'
                  ;(e.currentTarget as HTMLAnchorElement).style.color = 'var(--t-text-faint)'
                }
              }}
            >
              <Icon className="h-4 w-4" />
            </Link>
          )
        })}
      </nav>

      {/* User avatar + menu déconnexion */}
      <div className="pb-3 relative" ref={menuRef}>
        <button
          onClick={() => setMenuOpen((v) => !v)}
          title="Mon compte"
          className="w-7 h-7 rounded-full flex items-center justify-center transition-colors"
          style={{ backgroundColor: 'var(--t-bg-active)' }}
          onMouseEnter={e => (e.currentTarget as HTMLButtonElement).style.backgroundColor = 'var(--t-bg-button)'}
          onMouseLeave={e => (e.currentTarget as HTMLButtonElement).style.backgroundColor = 'var(--t-bg-active)'}
        >
          <span className="text-xs font-medium" style={{ color: 'var(--t-text)' }}>B</span>
        </button>

        {menuOpen && (
          <div
            className="absolute bottom-10 left-0 w-36 rounded-md shadow-lg overflow-hidden"
            style={{
              backgroundColor: 'var(--t-bg-card)',
              border: '1px solid var(--t-border)',
            }}
          >
            <button
              onClick={() => { setMenuOpen(false); logout() }}
              className="w-full flex items-center gap-2 px-3 py-2 text-xs transition-colors"
              style={{ color: '#ef4444' }}
              onMouseEnter={e => (e.currentTarget as HTMLButtonElement).style.backgroundColor = 'var(--t-bg-hover)'}
              onMouseLeave={e => (e.currentTarget as HTMLButtonElement).style.backgroundColor = 'transparent'}
            >
              <LogOut className="h-3 w-3" />
              Se déconnecter
            </button>
          </div>
        )}
      </div>
    </aside>
  )
}
