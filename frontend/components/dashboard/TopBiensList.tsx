import { Panel } from '@/components/ui/Panel'
import type { Bien } from '@/lib/types/dashboard'
import { formatCurrency } from '@/lib/utils/format'
import { Building2, MapPin, TrendingUp } from 'lucide-react'

interface TopBiensListProps {
  data: Bien[]
}

export function TopBiensList({ data = [] }: TopBiensListProps) {
  if (!data || data.length === 0) {
    return (
      <Panel title="Top 5 Biens" className="h-full">
        <div className="flex items-center justify-center py-12">
          <p className="text-sm text-muted-foreground">Aucun bien disponible</p>
        </div>
      </Panel>
    )
  }

  return (
    <Panel title="Top 5 Biens" className="h-full">
      <div className="space-y-3">
        {data.slice(0, 5).map((bien, index) => (
          <div
            key={bien.id}
            className="flex items-center gap-3 rounded-lg bg-secondary/30 p-3"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent/10 text-accent">
              <Building2 className="h-4 w-4" />
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-muted-foreground">
                  #{index + 1}
                </span>
                <span className="truncate text-sm font-medium text-foreground">
                  {bien.nom}
                </span>
              </div>
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <MapPin className="h-3 w-3" />
                {bien.ville}
              </div>
            </div>

            <div className="text-right">
              <p className="font-mono text-sm font-medium tabular-nums text-foreground">
                {formatCurrency(bien.valeur, true)}
              </p>
              <div className="flex items-center justify-end gap-1 text-positive">
                <TrendingUp className="h-3 w-3" />
                <span className="font-mono text-xs tabular-nums">
                  {bien.rendement.toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Panel>
  )
}
