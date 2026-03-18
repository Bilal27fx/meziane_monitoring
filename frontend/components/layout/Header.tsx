'use client'

import { ThemeToggle } from './ThemeToggle'
import { Menu, Bell, Search } from 'lucide-react'
import { useUIStore } from '@/lib/stores/ui-store'

export function Header() {
  const { toggleSidebar } = useUIStore()

  return (
    <header className="sticky top-0 z-40 flex h-16 items-center justify-between border-b border-border/50 bg-background/95 px-6 backdrop-blur-md supports-[backdrop-filter]:bg-background/80">
      <div className="flex items-center gap-4">
        <button
          onClick={toggleSidebar}
          className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-all hover:bg-secondary/80 hover:text-foreground active:scale-95 lg:hidden"
          aria-label="Toggle sidebar"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div className="hidden items-center gap-3 rounded-xl border border-border/60 bg-secondary/40 px-4 py-2.5 shadow-sm transition-all hover:border-border hover:bg-secondary/60 focus-within:border-primary/40 focus-within:ring-2 focus-within:ring-primary/20 sm:flex">
          <Search className="h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Rechercher..."
            className="w-56 bg-transparent text-sm text-foreground placeholder:text-muted-foreground focus:outline-none"
          />
          <kbd className="hidden rounded-md bg-muted/80 px-2 py-1 text-xs font-medium text-muted-foreground shadow-sm md:inline">
            ⌘K
          </kbd>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button
          className="relative flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-all hover:bg-secondary/80 hover:text-foreground active:scale-95"
          aria-label="Notifications"
        >
          <Bell className="h-[18px] w-[18px]" />
          <span className="absolute -right-0.5 -top-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[10px] font-semibold text-primary-foreground shadow-sm ring-2 ring-background">
            3
          </span>
        </button>
        <ThemeToggle />
        <div className="ml-2 flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-primary to-primary/80 text-sm font-semibold text-primary-foreground shadow-md ring-2 ring-primary/20 transition-all hover:shadow-lg hover:ring-primary/30">
          M
        </div>
      </div>
    </header>
  )
}
