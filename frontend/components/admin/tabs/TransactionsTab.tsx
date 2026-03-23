'use client'

import { useState } from 'react'
import { Plus, Download, CheckCircle, XCircle, Pencil } from 'lucide-react'
import { useTransactions, useValidateTransaction, useRejectTransaction, useSCIs } from '@/lib/hooks/useAdmin'
import DataTable, { Column } from '@/components/ui/DataTable'
import Badge from '@/components/ui/Badge'
import { formatCurrency, formatDate } from '@/lib/utils/format'
import toast from 'react-hot-toast'
import type { Transaction } from '@/lib/types'

const CATEGORIES = ['Loyer', 'Charges', 'Taxe', 'Assurance', 'Travaux', 'Frais', 'Autre']

export default function TransactionsTab() {
  const [page, setPage] = useState(1)
  const [sciFilter, setSciFilter] = useState('')
  const [catFilter, setCatFilter] = useState('')
  const [statutFilter, setStatutFilter] = useState('')

  const { data, isLoading } = useTransactions({
    page,
    per_page: 20,
    sci_id: sciFilter ? Number(sciFilter) : undefined,
    categorie: catFilter || undefined,
    statut: statutFilter || undefined,
  })
  const { data: scisData } = useSCIs()
  const validate = useValidateTransaction()
  const reject = useRejectTransaction()

  const transactions = data?.items ?? []
  const scis = scisData?.items ?? []

  const statutVariant = (statut: string) => {
    if (statut === 'valide') return 'ok' as const
    if (statut === 'en_attente') return 'warning' as const
    return 'error' as const
  }

  const columns: Column<Transaction>[] = [
    { header: 'Date', accessor: 'date', render: (t) => <span className="font-mono text-[10px] text-[#a3a3a3]">{formatDate(t.date)}</span> },
    { header: 'SCI', accessor: 'sci_id', render: (t) => <span className="text-xs text-[#737373]">{scis.find((s) => s.id === t.sci_id)?.nom ?? '—'}</span> },
    { header: 'Libellé', accessor: 'libelle', render: (t) => <span className="text-xs text-white">{t.libelle}</span> },
    { header: 'Catégorie', accessor: 'categorie', render: (t) => <span className="bg-[#262626] text-[#a3a3a3] text-[9px] rounded px-1.5 py-0.5">{t.categorie}</span> },
    { header: 'Montant', accessor: 'montant', render: (t) => (
      <span className={`font-mono text-xs tabular-nums font-semibold ${t.montant >= 0 ? 'text-[#22c55e]' : 'text-[#ef4444]'}`}>
        {t.montant >= 0 ? '+' : ''}{formatCurrency(t.montant)}
      </span>
    )},
    { header: 'Statut', accessor: 'statut', render: (t) => <Badge variant={statutVariant(t.statut)} dot>{t.statut === 'valide' ? 'Validé' : t.statut === 'en_attente' ? 'En attente' : 'Rejeté'}</Badge> },
    { header: 'Actions', accessor: 'id', render: (t) => (
      <div className="flex items-center gap-1">
        {t.statut === 'en_attente' && (
          <>
            <button onClick={() => { validate.mutate(t.id); toast.success('Transaction validée') }} className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-[#22c55e] hover:bg-[#22c55e]/10 transition-colors" title="Valider">
              <CheckCircle className="h-3 w-3" />
            </button>
            <button onClick={() => { reject.mutate(t.id); toast.success('Transaction rejetée') }} className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-[#ef4444] hover:bg-[#ef4444]/10 transition-colors" title="Rejeter">
              <XCircle className="h-3 w-3" />
            </button>
          </>
        )}
        <button className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-white hover:bg-[#262626] transition-colors">
          <Pencil className="h-3 w-3" />
        </button>
      </div>
    )},
  ]

  // Summary
  const revenus = transactions.filter((t) => t.montant > 0).reduce((s, t) => s + t.montant, 0)
  const depenses = transactions.filter((t) => t.montant < 0).reduce((s, t) => s + t.montant, 0)
  const net = revenus + depenses

  return (
    <div className="space-y-3">
      {/* Header + filters */}
      <div className="flex items-center gap-2 flex-wrap">
        <h2 className="text-xs font-semibold text-white uppercase tracking-wider">Transactions</h2>
        <div className="flex items-center gap-2 ml-auto">
          {[
            { value: sciFilter, onChange: setSciFilter, options: [{ label: 'Toutes SCI', value: '' }, ...scis.map((s) => ({ label: s.nom, value: String(s.id) }))] },
            { value: catFilter, onChange: setCatFilter, options: [{ label: 'Toutes catégories', value: '' }, ...CATEGORIES.map((c) => ({ label: c, value: c }))] },
            { value: statutFilter, onChange: setStatutFilter, options: [{ label: 'Tous statuts', value: '' }, { label: 'Validé', value: 'valide' }, { label: 'En attente', value: 'en_attente' }, { label: 'Rejeté', value: 'rejete' }] },
          ].map((sel, i) => (
            <select
              key={i}
              value={sel.value}
              onChange={(e) => sel.onChange(e.target.value)}
              className="h-7 text-xs bg-[#0d0d0d] border border-[#262626] rounded px-2 text-[#a3a3a3] focus:outline-none"
            >
              {sel.options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
          ))}
          <button onClick={() => toast.success('Export CSV en cours...')} className="flex items-center gap-1 h-7 px-2 bg-[#262626] text-[#a3a3a3] text-xs rounded hover:bg-[#404040] transition-colors">
            <Download className="h-3 w-3" />
            CSV
          </button>
          <button className="flex items-center gap-1.5 h-7 px-3 bg-white text-black text-xs font-medium rounded hover:bg-[#e5e5e5] transition-colors">
            <Plus className="h-3 w-3" />
            Ajouter
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-[#111111] border border-[#262626] rounded-md p-3">
        <DataTable
          columns={columns}
          data={transactions}
          loading={isLoading}
          emptyMessage="Aucune transaction"
          rowKey={(r) => r.id}
          pagination={data ? {
            page,
            totalPages: data.pages,
            total: data.total,
            onPageChange: setPage,
          } : undefined}
        />
      </div>

      {/* Summary bar */}
      <div className="grid grid-cols-3 gap-2">
        {[
          { label: 'Revenus', value: revenus, color: 'text-[#22c55e]' },
          { label: 'Dépenses', value: depenses, color: 'text-[#ef4444]' },
          { label: 'Net', value: net, color: net >= 0 ? 'text-[#22c55e]' : 'text-[#ef4444]' },
        ].map(({ label, value, color }) => (
          <div key={label} className="bg-[#111111] border border-[#262626] rounded-md p-3">
            <p className="text-[9px] text-[#525252] uppercase tracking-wide">{label}</p>
            <p className={`text-sm font-mono font-semibold tabular-nums mt-1 ${color}`}>
              {value >= 0 ? '+' : ''}{formatCurrency(value)}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}
