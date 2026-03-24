'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState, useRef, useEffect } from 'react'
import { LayoutGrid, Zap, Settings2, LogOut } from 'lucide-react'
import { cn } from '@/lib/utils/cn'
import { useAuth } from '@/lib/hooks/useAuth'

const NAV_ITEMS = [
  { href: '/dashboard', icon: LayoutGrid, label: 'Dashboard' },
  { href: '/agent', icon: Zap, label: 'Agent IA' },
  { href: '/admin', icon: Settings2, label: 'Administration' },
]

export default function Sidebar() {
  const pathname = usePathname()
  const { logout } = useAuth()
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
    <aside className="fixed left-0 top-0 h-screen w-12 z-20 bg-[#0d0d0d] border-r border-[#262626] flex flex-col items-center">
      {/* Logo → Dashboard */}
      <Link
        href="/dashboard"
        className="h-14 flex items-center justify-center w-full border-b border-[#262626] hover:bg-[#1a1a1a] transition-colors"
        title="Dashboard"
      >
        <span className="text-sm font-bold text-white">M</span>
      </Link>

      {/* Nav */}
      <nav className="flex flex-col items-center gap-1 pt-2 flex-1">
        {NAV_ITEMS.map(({ href, icon: Icon, label }) => {
          const isActive = pathname === href || pathname.startsWith(href + '/')
          return (
            <Link
              key={href}
              href={href}
              title={label}
              className={cn(
                'w-10 h-10 mx-auto rounded-md flex items-center justify-center transition-colors',
                isActive
                  ? 'bg-[#262626] text-white'
                  : 'text-[#525252] hover:text-white hover:bg-[#1a1a1a]'
              )}
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
          className="w-7 h-7 rounded-full bg-[#262626] hover:bg-[#333333] flex items-center justify-center transition-colors"
        >
          <span className="text-xs font-medium text-white">B</span>
        </button>

        {menuOpen && (
          <div className="absolute bottom-10 left-0 w-36 bg-[#111111] border border-[#262626] rounded-md shadow-lg overflow-hidden">
            <button
              onClick={() => { setMenuOpen(false); logout() }}
              className="w-full flex items-center gap-2 px-3 py-2 text-xs text-[#ef4444] hover:bg-[#1a1a1a] transition-colors"
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
