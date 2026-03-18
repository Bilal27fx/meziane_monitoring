import { Panel } from '@/components/ui/Panel'
import type { Locataire } from '@/lib/types/dashboard'
import { formatCurrency, formatDateFull } from '@/lib/utils/format'
import { cn } from '@/lib/utils'
import { User, Calendar, AlertTriangle, CheckCircle } from 'lucide-react'

interface LocatairesListProps {
  data: Locataire[]
}

const statutConfig: Record<Locataire['statut'], { label: string; class: string; icon: typeof CheckCircle }> = {
  OK: { label: 'A jour', class: 'text-positive bg-positive/10', icon: CheckCircle },
  RETARD: { label: 'Retard', class: 'text-warning bg-warning/10', icon: AlertTriangle },
  IMPAYE: { label: 'Impaye', class: 'text-negative bg-negative/10', icon: AlertTriangle },
}

export function LocatairesList({ data = [] }: LocatairesListProps) {
  if (!data || data.length === 0) {
    return (
      <Panel title="Locataires" className="h-full">
        <div className="flex items-center justify-center py-12">
          <p className="text-sm text-muted-foreground">Aucun locataire disponible</p>
        </div>
      </Panel>
    )
  }

  return (
    <Panel title="Locataires" className="h-full">
      <div className="space-y-2">
        {data.slice(0, 5).map((locataire) => {
          const statut = statutConfig[locataire.statut]
          const StatusIcon = statut.icon
          
          return (
            <div
              key={locataire.id}
              className="flex items-center gap-3 rounded-lg bg-secondary/30 p-3"
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted text-muted-foreground">
                <User className="h-4 w-4" />
              </div>
              
              <div className="flex-1 min-w-0">
                <p className="truncate text-sm font-medium text-foreground">
                  {locataire.nom}
                </p>
                <p className="truncate text-xs text-muted-foreground">
                  {locataire.bien}
                </p>
              </div>

              <div className="text-right">
                <p className="font-mono text-sm font-medium tabular-nums text-foreground">
                  {formatCurrency(locataire.loyer)}
                </p>
                <div className="flex items-center justify-end gap-1 text-xs text-muted-foreground">
                  <Calendar className="h-3 w-3" />
                  {formatDateFull(locataire.finBail)}
                </div>
              </div>

              <div
                className={cn(
                  'flex items-center gap-1 rounded px-2 py-1 text-xs font-medium',
                  statut.class
                )}
              >
                <StatusIcon className="h-3 w-3" />
                {statut.label}
              </div>
            </div>
          )
        })}
      </div>
    </Panel>
  )
}
