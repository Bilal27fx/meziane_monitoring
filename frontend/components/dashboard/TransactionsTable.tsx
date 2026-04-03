import Link from 'next/link'
import { formatDate, formatCurrency } from '@/lib/utils/format'
import Badge from '@/components/ui/Badge'
import type { DashboardTransaction } from '@/lib/types'

interface TransactionsTableProps {
  data?: DashboardTransaction[]
}


function statutBadge(statut: string) {
  if (statut === 'valide' || statut === 'validated') return <Badge variant="ok" dot>Validé</Badge>
  if (statut === 'en_attente' || statut === 'pending') return <Badge variant="warning" dot>En attente</Badge>
  return <Badge variant="error" dot>Rejeté</Badge>
}

export default function TransactionsTable({ data = [] }: TransactionsTableProps) {
  const rows = data.slice(0, 8)

  return (
    <div className="p-3.5 bg-[#111111] border border-[#262626] rounded-lg flex flex-col hover:border-[#404040] transition-colors">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs text-[#a3a3a3] uppercase tracking-widest font-medium">Transactions récentes</span>
        <Link href="/admin?tab=transactions" className="text-xs text-[#737373] hover:text-white transition-colors font-medium">
          Voir toutes →
        </Link>
      </div>
      <div className="overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-[#262626]">
              <th className="text-left text-xs text-[#737373] uppercase tracking-wider py-2 px-2">Date</th>
              <th className="text-left text-xs text-[#737373] uppercase tracking-wider py-2 px-2">SCI</th>
              <th className="text-left text-xs text-[#737373] uppercase tracking-wider py-2 px-2">Libellé</th>
              <th className="text-left text-xs text-[#737373] uppercase tracking-wider py-2 px-2">Catégorie</th>
              <th className="text-right text-xs text-[#737373] uppercase tracking-wider py-2 px-2">Montant</th>
              <th className="text-right text-xs text-[#737373] uppercase tracking-wider py-2 px-2">Statut</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((tx) => (
              <tr key={tx.id} className="border-b border-[#1f1f1f] hover:bg-[#1a1a1a] transition-colors">
                <td className="py-2 px-2">
                  <span className="font-mono text-xs text-[#d4d4d4]">{formatDate(tx.date)}</span>
                </td>
                <td className="py-2 px-2">
                  <span className="text-xs text-[#a3a3a3] truncate">{tx.sci_nom ?? '—'}</span>
                </td>
                <td className="py-2 px-2 max-w-0">
                  <span className="text-xs text-white block truncate font-medium">{tx.libelle}</span>
                </td>
                <td className="py-2 px-2">
                  <span className="bg-[#262626] text-[#d4d4d4] text-xs rounded-md px-2 py-0.5">{tx.categorie}</span>
                </td>
                <td className="py-2 px-2 text-right">
                  <span
                    className={`font-mono font-semibold text-sm tabular-nums ${
                      tx.montant >= 0 ? 'text-[#22c55e]' : 'text-[#ef4444]'
                    }`}
                  >
                    {tx.montant >= 0 ? '+' : ''}{formatCurrency(tx.montant)}
                  </span>
                </td>
                <td className="py-2 px-2 text-right">
                  {statutBadge(tx.statut_validation)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
