import Link from 'next/link'
import { formatDate, formatCurrency } from '@/lib/utils/format'
import Badge from '@/components/ui/Badge'
import type { Transaction } from '@/lib/types'

interface TransactionsTableProps {
  data?: Transaction[]
}


function statutBadge(statut: string) {
  if (statut === 'valide') return <Badge variant="ok" dot>Validé</Badge>
  if (statut === 'en_attente') return <Badge variant="warning" dot>En attente</Badge>
  return <Badge variant="error" dot>Rejeté</Badge>
}

export default function TransactionsTable({ data = [] }: TransactionsTableProps) {
  const rows = data.slice(0, 7)

  return (
    <div className="h-48 p-2 bg-[#111111] border border-[#262626] rounded-md flex flex-col">
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-[10px] text-[#737373] uppercase tracking-wide">Transactions récentes</span>
        <Link href="/admin" className="text-[9px] text-[#525252] hover:text-white transition-colors">
          Voir toutes →
        </Link>
      </div>
      <div className="flex-1 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-[#262626]">
              <th className="text-left text-[9px] text-[#525252] uppercase tracking-wider py-1 px-1">Date</th>
              <th className="text-left text-[9px] text-[#525252] uppercase tracking-wider py-1 px-1">SCI</th>
              <th className="text-left text-[9px] text-[#525252] uppercase tracking-wider py-1 px-1">Libellé</th>
              <th className="text-left text-[9px] text-[#525252] uppercase tracking-wider py-1 px-1">Catégorie</th>
              <th className="text-right text-[9px] text-[#525252] uppercase tracking-wider py-1 px-1">Montant</th>
              <th className="text-right text-[9px] text-[#525252] uppercase tracking-wider py-1 px-1">Statut</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((tx) => (
              <tr key={tx.id} className="border-b border-[#262626]/40 hover:bg-[#1a1a1a] transition-colors">
                <td className="py-1 px-1">
                  <span className="font-mono text-[10px] text-[#a3a3a3]">{formatDate(tx.date)}</span>
                </td>
                <td className="py-1 px-1">
                  <span className="text-[10px] text-[#737373] truncate">{tx.sci?.nom ?? `SCI #${tx.sci_id}`}</span>
                </td>
                <td className="py-1 px-1 max-w-0">
                  <span className="text-[10px] text-white block truncate">{tx.libelle}</span>
                </td>
                <td className="py-1 px-1">
                  <span className="bg-[#262626] text-[#a3a3a3] text-[9px] rounded px-1 py-0.5">{tx.categorie}</span>
                </td>
                <td className="py-1 px-1 text-right">
                  <span
                    className={`font-mono font-semibold text-xs tabular-nums ${
                      tx.montant >= 0 ? 'text-[#22c55e]' : 'text-[#ef4444]'
                    }`}
                  >
                    {tx.montant >= 0 ? '+' : ''}{formatCurrency(tx.montant)}
                  </span>
                </td>
                <td className="py-1 px-1 text-right">
                  {statutBadge(tx.statut)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
