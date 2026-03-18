import { Panel } from '@/components/ui/Panel'
import type { SCI } from '@/lib/types/dashboard'
import { formatCurrency } from '@/lib/utils/format'
import { Building, Wallet } from 'lucide-react'

interface SCIOverviewGridProps {
  data: SCI[]
}

export function SCIOverviewGrid({ data = [] }: SCIOverviewGridProps) {
  if (!data || data.length === 0) {
    return (
      <Panel title="SCI Overview" className="h-full">
        <div className="flex items-center justify-center py-12">
          <p className="text-sm text-muted-foreground">Aucune SCI disponible</p>
        </div>
      </Panel>
    )
  }

  return (
    <Panel title="SCI Overview" className="h-full">
      <div className="grid gap-3">
        {data.map((sci) => (
          <div
            key={sci.id}
            className="rounded-lg border border-border bg-secondary/20 p-4"
          >
            <div className="flex items-start justify-between">
              <div>
                <h4 className="text-sm font-medium text-foreground">
                  {sci.nom}
                </h4>
                <p className="mt-1 text-xs text-muted-foreground">
                  {sci.nbBiens} bien{sci.nbBiens > 1 ? 's' : ''}
                </p>
              </div>
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent/10 text-accent">
                <Building className="h-4 w-4" />
              </div>
            </div>
            
            <div className="mt-4 grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-muted-foreground">Valeur totale</p>
                <p className="mt-1 font-mono text-sm font-medium tabular-nums text-foreground">
                  {formatCurrency(sci.valeur, true)}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Cashflow/mois</p>
                <div className="mt-1 flex items-center gap-1 text-positive">
                  <Wallet className="h-3 w-3" />
                  <span className="font-mono text-sm font-medium tabular-nums">
                    +{formatCurrency(sci.cashflow)}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Panel>
  )
}
