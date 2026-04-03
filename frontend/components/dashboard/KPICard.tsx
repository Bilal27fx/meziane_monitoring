import { cn } from '@/lib/utils/cn'

interface KPICardProps {
  title: string
  value: string
  change?: number
  trend?: 'up' | 'down' | 'neutral'
  icon?: React.ElementType
  subtitle?: string
}

export default function KPICard({ title, value, change, trend, icon: Icon, subtitle }: KPICardProps) {
  const showChange = change !== undefined && change !== 0

  return (
    <div className="h-20 p-3.5 bg-[#111111] border border-[#262626] rounded-lg flex items-center gap-3.5 hover:border-[#404040] transition-colors">
      {Icon && (
        <div className="flex-shrink-0 w-8 h-8 rounded-md bg-[#1a1a1a] flex items-center justify-center">
          <Icon className="h-4 w-4 text-[#a3a3a3]" />
        </div>
      )}
      <div className="flex flex-col min-w-0 flex-1">
        <span className="text-xs text-[#a3a3a3] uppercase tracking-widest truncate font-medium">{title}</span>
        <div className="flex items-baseline gap-2 mt-1">
          <span className="text-xl font-semibold font-mono text-white tabular-nums leading-none">
            {value}
          </span>
          {showChange && (
            <span
              className={cn(
                'text-xs font-mono flex-shrink-0',
                trend === 'up' ? 'text-[#22c55e]' : trend === 'down' ? 'text-[#ef4444]' : 'text-[#737373]'
              )}
            >
              {trend === 'up' ? '▲' : trend === 'down' ? '▼' : '·'}{' '}
              {change > 0 ? '+' : ''}{change.toFixed(1)}%
            </span>
          )}
        </div>
        {subtitle && (
          <span className="text-[11px] text-[#737373] truncate mt-0.5">{subtitle}</span>
        )}
      </div>
    </div>
  )
}
