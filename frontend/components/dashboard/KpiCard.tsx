import { cn } from '@/lib/utils'
import { formatCurrency, formatNumber } from '@/lib/utils/format'
import type { KpiData } from '@/lib/types/dashboard'
import { TrendingUp, TrendingDown, AlertCircle, Activity } from 'lucide-react'

interface KpiCardProps {
  data: KpiData
  icon?: 'trending' | 'alert' | 'activity'
}

export function KpiCard({ data, icon = 'trending' }: KpiCardProps) {
  const isPositive = data.change >= 0
  
  const formatValue = () => {
    if (data.suffix === '%') {
      return data.value.toFixed(1) + '%'
    }
    if (data.suffix === ' EUR') {
      return formatCurrency(data.value, true)
    }
    return formatNumber(data.value)
  }

  const IconComponent = {
    trending: isPositive ? TrendingUp : TrendingDown,
    alert: AlertCircle,
    activity: Activity,
  }[icon]

  return (
    <div className="glass rounded-2xl border border-border/60 p-6 shadow-sm transition-all hover:border-border/80 hover:shadow-md">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            {data.label}
          </p>
          <p className="mt-3 font-mono text-3xl font-bold tabular-nums text-foreground">
            {data.prefix}{formatValue()}
          </p>
        </div>
        <div
          className={cn(
            'flex h-10 w-10 items-center justify-center rounded-xl shadow-sm transition-all hover:scale-105',
            icon === 'alert'
              ? 'bg-warning/15 text-warning ring-1 ring-warning/20'
              : isPositive
                ? 'bg-positive/15 text-positive ring-1 ring-positive/20'
                : 'bg-negative/15 text-negative ring-1 ring-negative/20'
          )}
        >
          <IconComponent className="h-5 w-5" />
        </div>
      </div>

      <div className="mt-4 flex items-center gap-2">
        <span
          className={cn(
            'font-mono text-sm font-semibold tabular-nums',
            icon === 'alert'
              ? 'text-warning'
              : isPositive ? 'text-positive' : 'text-negative'
          )}
        >
          {isPositive ? '+' : ''}{data.change}
          {typeof data.change === 'number' && data.label !== 'Alertes IA' ? '%' : ''}
        </span>
        <span className="text-sm text-muted-foreground">
          {data.changeLabel}
        </span>
      </div>
    </div>
  )
}
