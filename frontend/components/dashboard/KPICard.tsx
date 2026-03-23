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
    <div className="h-14 p-2.5 bg-[#111111] border border-[#262626] rounded-md flex items-center gap-3">
      {Icon && (
        <div className="flex-shrink-0">
          <Icon className="h-3.5 w-3.5 text-[#525252]" />
        </div>
      )}
      <div className="flex flex-col min-w-0 flex-1">
        <span className="text-[10px] text-[#737373] uppercase tracking-wide truncate">{title}</span>
        <div className="flex items-baseline gap-1.5 mt-0.5">
          <span className="text-base font-semibold font-mono text-white tabular-nums leading-none">
            {value}
          </span>
          {showChange && (
            <span
              className={cn(
                'text-[10px] font-mono flex-shrink-0',
                trend === 'up' ? 'text-[#22c55e]' : trend === 'down' ? 'text-[#ef4444]' : 'text-[#737373]'
              )}
            >
              {trend === 'up' ? '▲' : trend === 'down' ? '▼' : '·'}{' '}
              {change > 0 ? '+' : ''}{change.toFixed(1)}%
            </span>
          )}
        </div>
        {subtitle && (
          <span className="text-[9px] text-[#525252] truncate">{subtitle}</span>
        )}
      </div>
    </div>
  )
}
