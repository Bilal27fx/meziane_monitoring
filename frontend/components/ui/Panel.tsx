import { cn } from '@/lib/utils'
import { ReactNode } from 'react'

interface PanelProps {
  children: ReactNode
  className?: string
  title?: string
  compact?: boolean
}

export function Panel({ children, className, title, compact = false }: PanelProps) {
  return (
    <div
      className={cn(
        'glass rounded-2xl border border-border/60 shadow-sm transition-all hover:border-border/80 hover:shadow-md',
        compact ? 'p-5' : 'p-6',
        className
      )}
    >
      {title && (
        <h3 className="mb-4 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          {title}
        </h3>
      )}
      {children}
    </div>
  )
}
