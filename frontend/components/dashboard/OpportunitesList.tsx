import { Panel } from '@/components/ui/Panel'
import type { Opportunite } from '@/lib/types/dashboard'
import { cn } from '@/lib/utils'
import { Sparkles, PiggyBank, Receipt, TrendingUp, ChevronRight } from 'lucide-react'

interface OpportunitesListProps {
  data: Opportunite[]
}

const typeConfig: Record<string, { icon: typeof Sparkles; class: string }> = {
  ECONOMIE: { icon: PiggyBank, class: 'text-positive bg-positive/10' },
  FISCAL: { icon: Receipt, class: 'text-warning bg-warning/10' },
  REVENU: { icon: TrendingUp, class: 'text-accent bg-accent/10' },
}

export function OpportunitesList({ data = [] }: OpportunitesListProps) {
  if (!data || data.length === 0) {
    return (
      <Panel title="Opportunites IA" className="h-full">
        <div className="flex items-center justify-center py-12">
          <p className="text-sm text-muted-foreground">Aucune opportunité détectée</p>
        </div>
      </Panel>
    )
  }

  return (
    <Panel title="Opportunites IA" className="h-full">
      <div className="space-y-3">
        {data.map((opp) => {
          const config = typeConfig[opp.type] || { icon: Sparkles, class: 'text-accent bg-accent/10' }
          const Icon = config.icon

          return (
            <div
              key={opp.id}
              className="group cursor-pointer rounded-lg border border-border bg-secondary/20 p-3 transition-colors hover:bg-secondary/40"
            >
              <div className="flex items-start gap-3">
                <div
                  className={cn(
                    'flex h-8 w-8 items-center justify-center rounded-lg',
                    config.class
                  )}
                >
                  <Icon className="h-4 w-4" />
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-medium text-foreground">
                      {opp.titre}
                    </h4>
                    <div className="flex items-center gap-1">
                      <span className="font-mono text-xs font-medium tabular-nums text-accent">
                        {opp.score}%
                      </span>
                      <ChevronRight className="h-4 w-4 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100" />
                    </div>
                  </div>
                  <p className="mt-1 text-xs text-muted-foreground line-clamp-2">
                    {opp.description}
                  </p>
                </div>
              </div>

              {/* Score bar */}
              <div className="mt-3 h-1 overflow-hidden rounded-full bg-secondary">
                <div
                  className="h-full rounded-full bg-accent transition-all"
                  style={{ width: `${opp.score}%` }}
                />
              </div>
            </div>
          )
        })}
      </div>
    </Panel>
  )
}
