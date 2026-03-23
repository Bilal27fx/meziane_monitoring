'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { LayoutGrid, Zap, Settings2 } from 'lucide-react'
import { cn } from '@/lib/utils/cn'

const NAV_ITEMS = [
  { href: '/dashboard', icon: LayoutGrid, label: 'Dashboard' },
  { href: '/agent', icon: Zap, label: 'Agent IA' },
  { href: '/admin', icon: Settings2, label: 'Administration' },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="fixed left-0 top-0 h-screen w-12 z-20 bg-[#0d0d0d] border-r border-[#262626] flex flex-col items-center">
      {/* Logo */}
      <div className="h-14 flex items-center justify-center w-full border-b border-[#262626]">
        <span className="text-sm font-bold text-white">M</span>
      </div>

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

      {/* User avatar */}
      <div className="pb-3">
        <div className="w-7 h-7 rounded-full bg-[#262626] flex items-center justify-center">
          <span className="text-xs font-medium text-white">B</span>
        </div>
      </div>
    </aside>
  )
}
