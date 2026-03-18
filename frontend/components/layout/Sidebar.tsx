'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { useUIStore } from '@/lib/stores/ui-store'
import {
  LayoutDashboard,
  Bot,
  Settings,
  Building2,
  Users,
  BarChart3,
  X,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react'

const navItems = [
  {
    label: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    label: 'Agents IA',
    href: '/agents',
    icon: Bot,
  },
  {
    label: 'Admin',
    href: '/admin',
    icon: Settings,
    children: [
      { label: 'Biens', href: '/admin/biens', icon: Building2 },
      { label: 'SCI', href: '/admin/sci', icon: BarChart3 },
      { label: 'Locataires', href: '/admin/locataires', icon: Users },
      { label: 'Analytics', href: '/admin/analytics', icon: BarChart3 },
    ],
  },
]

export function Sidebar() {
  const pathname = usePathname()
  const { sidebarOpen, setSidebarOpen, sidebarCollapsed, toggleSidebarCollapse } = useUIStore()

  return (
    <>
      {/* Overlay mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed left-0 top-0 z-50 flex h-full flex-col border-r border-sidebar-border bg-sidebar transition-all duration-300 lg:static lg:translate-x-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full',
          sidebarCollapsed ? 'w-16' : 'w-64'
        )}
      >
        {/* Logo & Controls */}
        <div className={cn(
          "flex h-16 items-center border-b border-sidebar-border/50",
          sidebarCollapsed ? "justify-center px-2" : "justify-between px-4"
        )}>
          {!sidebarCollapsed ? (
            <>
              <Link href="/dashboard" className="flex items-center gap-2">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-primary/80 shadow-md ring-2 ring-primary/20">
                  <BarChart3 className="h-4 w-4 text-primary-foreground" />
                </div>
                <span className="text-sm font-semibold text-sidebar-foreground">
                  Meziane
                </span>
              </Link>

              {/* Mobile close button */}
              <button
                onClick={() => setSidebarOpen(false)}
                className="flex h-8 w-8 items-center justify-center rounded-lg text-sidebar-foreground/60 hover:bg-sidebar-accent lg:hidden"
              >
                <X className="h-4 w-4" />
              </button>

              {/* Desktop collapse toggle */}
              <button
                onClick={toggleSidebarCollapse}
                className="hidden h-8 w-8 items-center justify-center rounded-lg text-sidebar-foreground/60 transition-all hover:bg-sidebar-accent hover:text-sidebar-foreground active:scale-95 lg:flex"
                title="Collapse sidebar"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
            </>
          ) : (
            /* Collapsed state - only expand button */
            <button
              onClick={toggleSidebarCollapse}
              className="hidden h-9 w-9 items-center justify-center rounded-xl text-sidebar-foreground/60 transition-all hover:bg-sidebar-accent hover:text-sidebar-foreground active:scale-95 lg:flex"
              title="Expand sidebar"
            >
              <ChevronRight className="h-5 w-5" />
            </button>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto p-3">
          <ul className="space-y-1">
            {navItems.map((item) => {
              const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
              const Icon = item.icon

              return (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className={cn(
                      'flex items-center rounded-lg px-3 py-2.5 text-sm font-medium transition-all hover:scale-[1.02]',
                      sidebarCollapsed ? 'justify-center' : 'gap-3',
                      isActive
                        ? 'bg-sidebar-accent text-sidebar-primary shadow-sm'
                        : 'text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-foreground'
                    )}
                    title={sidebarCollapsed ? item.label : undefined}
                    onClick={sidebarCollapsed ? toggleSidebarCollapse : undefined}
                  >
                    <Icon className="h-4 w-4 shrink-0" />
                    {!sidebarCollapsed && <span>{item.label}</span>}
                  </Link>

                  {/* Sub-items */}
                  {item.children && isActive && !sidebarCollapsed && (
                    <ul className="ml-4 mt-1 space-y-1 border-l border-sidebar-border pl-3">
                      {item.children.map((child) => {
                        const ChildIcon = child.icon
                        const isChildActive = pathname === child.href

                        return (
                          <li key={child.href}>
                            <Link
                              href={child.href}
                              className={cn(
                                'flex items-center gap-2 rounded-lg px-2 py-1.5 text-xs transition-colors',
                                isChildActive
                                  ? 'text-sidebar-primary'
                                  : 'text-sidebar-foreground/60 hover:text-sidebar-foreground'
                              )}
                            >
                              <ChildIcon className="h-3 w-3" />
                              {child.label}
                            </Link>
                          </li>
                        )
                      })}
                    </ul>
                  )}
                </li>
              )
            })}
          </ul>
        </nav>

        {/* Footer */}
        <div className="border-t border-sidebar-border/50 p-3">
          <div className={cn(
            "flex items-center gap-3 rounded-lg bg-sidebar-accent/50 px-3 py-2 transition-all",
            sidebarCollapsed && "justify-center px-0"
          )}>
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-primary to-primary/80 text-xs font-semibold text-primary-foreground shadow-md ring-2 ring-primary/20">
              M
            </div>
            {!sidebarCollapsed && (
              <div className="flex-1 overflow-hidden">
                <p className="truncate text-xs font-medium text-sidebar-foreground">
                  Meziane Family
                </p>
                <p className="truncate text-[10px] text-sidebar-foreground/60">
                  Premium
                </p>
              </div>
            )}
          </div>
        </div>
      </aside>
    </>
  )
}
