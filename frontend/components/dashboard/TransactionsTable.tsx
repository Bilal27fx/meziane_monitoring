import { Panel } from '@/components/ui/Panel'
import type { Transaction } from '@/lib/types/dashboard'
import { formatCurrency, formatDate } from '@/lib/utils/format'
import { cn } from '@/lib/utils'
import { ArrowUpRight, ArrowDownRight } from 'lucide-react'

interface TransactionsTableProps {
  data: Transaction[]
}

const typeColors: Record<Transaction['type'], string> = {
  LOYER: 'text-positive',
  CHARGE: 'text-negative',
  TRAVAUX: 'text-warning',
  IMPOT: 'text-negative',
  AUTRE: 'text-muted-foreground',
}

const typeLabels: Record<Transaction['type'], string> = {
  LOYER: 'Loyer',
  CHARGE: 'Charge',
  TRAVAUX: 'Travaux',
  IMPOT: 'Impot',
  AUTRE: 'Autre',
}

export function TransactionsTable({ data = [] }: TransactionsTableProps) {
  if (!data || data.length === 0) {
    return (
      <Panel title="Transactions Recentes" className="h-full">
        <div className="flex items-center justify-center py-12">
          <p className="text-sm text-muted-foreground">Aucune transaction disponible</p>
        </div>
      </Panel>
    )
  }

  return (
    <Panel title="Transactions Recentes" className="h-full overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border text-left">
              <th className="pb-2 text-xs font-medium text-muted-foreground">Date</th>
              <th className="pb-2 text-xs font-medium text-muted-foreground">Type</th>
              <th className="pb-2 text-xs font-medium text-muted-foreground">Description</th>
              <th className="pb-2 text-right text-xs font-medium text-muted-foreground">Montant</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {data.slice(0, 6).map((tx) => (
              <tr key={tx.id} className="group">
                <td className="py-2.5 font-mono text-xs tabular-nums text-muted-foreground">
                  {formatDate(tx.date)}
                </td>
                <td className="py-2.5">
                  <span
                    className={cn(
                      'inline-flex items-center rounded px-1.5 py-0.5 text-xs font-medium',
                      typeColors[tx.type],
                      'bg-current/10'
                    )}
                  >
                    {typeLabels[tx.type]}
                  </span>
                </td>
                <td className="max-w-[180px] truncate py-2.5 text-xs text-foreground">
                  {tx.description}
                </td>
                <td className="py-2.5 text-right">
                  <span
                    className={cn(
                      'inline-flex items-center gap-1 font-mono text-xs font-medium tabular-nums',
                      tx.montant >= 0 ? 'text-positive' : 'text-negative'
                    )}
                  >
                    {tx.montant >= 0 ? (
                      <ArrowUpRight className="h-3 w-3" />
                    ) : (
                      <ArrowDownRight className="h-3 w-3" />
                    )}
                    {formatCurrency(Math.abs(tx.montant))}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Panel>
  )
}
