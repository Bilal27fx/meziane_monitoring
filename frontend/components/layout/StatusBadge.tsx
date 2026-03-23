import { cn } from '@/lib/utils/cn'

type Status = 'online' | 'offline' | 'degraded' | 'unknown'

interface StatusBadgeProps {
  status: Status
  label?: string
  className?: string
}

const statusConfig: Record<Status, { dot: string; text: string; label: string }> = {
  online: { dot: 'bg-[#22c55e]', text: 'text-[#22c55e]', label: 'En ligne' },
  offline: { dot: 'bg-[#ef4444]', text: 'text-[#ef4444]', label: 'Hors ligne' },
  degraded: { dot: 'bg-[#eab308] animate-pulse', text: 'text-[#eab308]', label: 'Dégradé' },
  unknown: { dot: 'bg-[#525252]', text: 'text-[#737373]', label: 'Inconnu' },
}

export default function StatusBadge({ status, label, className }: StatusBadgeProps) {
  const config = statusConfig[status]
  return (
    <div className={cn('flex items-center gap-1.5', className)}>
      <span className={cn('w-1.5 h-1.5 rounded-full flex-shrink-0', config.dot)} />
      <span className={cn('text-[9px]', config.text)}>{label ?? config.label}</span>
    </div>
  )
}
