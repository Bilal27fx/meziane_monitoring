'use client'

import { cn } from '@/lib/utils/cn'

type BadgeVariant = 'ok' | 'warning' | 'error' | 'info' | 'default'

interface BadgeProps {
  variant?: BadgeVariant
  children: React.ReactNode
  className?: string
  dot?: boolean
}

const variantStyles: Record<BadgeVariant, string> = {
  ok: 'bg-[#22c55e]/20 text-[#22c55e] border border-[#22c55e]/30',
  warning: 'bg-[#eab308]/20 text-[#eab308] border border-[#eab308]/30',
  error: 'bg-[#ef4444]/20 text-[#ef4444] border border-[#ef4444]/30',
  info: 'bg-[#3b82f6]/20 text-[#3b82f6] border border-[#3b82f6]/30',
  default: 'bg-[#262626] text-[#a3a3a3] border border-[#262626]',
}

const dotStyles: Record<BadgeVariant, string> = {
  ok: 'bg-[#22c55e]',
  warning: 'bg-[#eab308]',
  error: 'bg-[#ef4444]',
  info: 'bg-[#3b82f6]',
  default: 'bg-[#a3a3a3]',
}

export default function Badge({ variant = 'default', children, className, dot = false }: BadgeProps) {
  return (
    <span
      className={cn(
        'rounded-full px-1.5 py-0.5 text-[9px] font-medium inline-flex items-center gap-1',
        variantStyles[variant],
        className
      )}
    >
      {dot && (
        <span className={cn('w-1.5 h-1.5 rounded-full flex-shrink-0', dotStyles[variant])} />
      )}
      {children}
    </span>
  )
}
