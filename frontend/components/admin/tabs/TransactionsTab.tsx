'use client'

import { useState } from 'react'
import { Plus, Download, CheckCircle, XCircle, Pencil, X, Trash2 } from 'lucide-react'
import {
  useTransactions, useValidateTransaction, useRejectTransaction,
  useCreateTransaction, useUpdateTransaction, useDeleteTransaction, useSCIs,
} from '@/lib/hooks/useAdmin'
import DataTable, { Column } from '@/components/ui/DataTable'
import Badge from '@/components/ui/Badge'
import { formatCurrency, formatDate } from '@/lib/utils/format'
import toast from 'react-hot-toast'
import type { Transaction } from '@/lib/types'

const CATEGORIES = [
  { label: 'Loyer', value: 'loyer' },
  { label: 'Charges copro', value: 'charges_copro' },
  { label: 'Taxe foncière', value: 'taxe_fonciere' },
  { label: 'Travaux', value: 'travaux' },
  { label: 'Remboursement crédit', value: 'remboursement_credit' },
  { label: 'Assurance', value: 'assurance' },
  { label: 'Honoraires', value: 'honoraires' },
  { label: 'Frais bancaires', value: 'frais_bancaires' },
  { label: 'Autre', value: 'autre' },
]

type EditForm = { date: string; montant: string; libelle: string; categorie: string }
type CreateForm = EditForm & { sci_id: string; compte_bancaire_id: string }

const EMPTY_CREATE: CreateForm = { date: '', montant: '', libelle: '', categorie: '', sci_id: '', compte_bancaire_id: '' }

export default function TransactionsTab() {
  const [page, setPage] = useState(1)
  const [sciFilter, setSciFilter] = useState('')
  const [catFilter, setCatFilter] = useState('')
  const [statutFilter, setStatutFilter] = useState('')

  const [editingTx, setEditingTx] = useState<Transaction | null>(null)
  const [confirmDelete, setConfirmDelete] = useState<Transaction | null>(null)
  const [editForm, setEditForm] = useState<EditForm>({ date: '', montant: '', libelle: '', categorie: '' })
  const [showCreate, setShowCreate] = useState(false)
  const [createForm, setCreateForm] = useState<CreateForm>(EMPTY_CREATE)

  const { data, isLoading } = useTransactions({
    page, per_page: 20,
    sci_id: sciFilter ? Number(sciFilter) : undefined,
    categorie: catFilter || undefined,
    statut: statutFilter || undefined,
  })
  const { data: scisData } = useSCIs()
  const validate = useValidateTransaction()
  const reject = useRejectTransaction()
  const createTx = useCreateTransaction()
  const updateTx = useUpdateTransaction()
  const deleteTx = useDeleteTransaction()

  const transactions = data?.items ?? []
  const scis = scisData?.items ?? []

  const statutVariant = (statut: string) => {
    if (statut === 'valide') return 'ok' as const
    if (statut === 'en_attente') return 'warning' as const
    return 'error' as const
  }

  const openEdit = (t: Transaction) => {
    setEditingTx(t)
    setEditForm({
      date: t.date,
      montant: String(t.montant),
      libelle: t.libelle,
      categorie: t.categorie ?? '',
    })
  }

  const submitEdit = () => {
    if (!editingTx) return
    updateTx.mutate(
      { id: editingTx.id, data: { date: editForm.date, montant: Number(editForm.montant), libelle: editForm.libelle, categorie: editForm.categorie || undefined } },
      {
        onSuccess: () => { toast.success('Transaction mise à jour'); setEditingTx(null) },
        onError: () => toast.error('Erreur lors de la mise à jour'),
      }
    )
  }

  const submitCreate = () => {
    if (!createForm.date || !createForm.montant || !createForm.libelle || !createForm.sci_id || !createForm.compte_bancaire_id) {
      toast.error('Remplissez tous les champs obligatoires')
      return
    }
    createTx.mutate(
      {
        date: createForm.date,
        montant: Number(createForm.montant),
        libelle: createForm.libelle,
        categorie: createForm.categorie || undefined,
        sci_id: Number(createForm.sci_id),
        compte_bancaire_id: createForm.compte_bancaire_id,
      },
      {
        onSuccess: () => { toast.success('Transaction créée'); setShowCreate(false); setCreateForm(EMPTY_CREATE) },
        onError: () => toast.error('Erreur lors de la création'),
      }
    )
  }

  const exportCSV = () => {
    if (!transactions.length) { toast.error('Aucune donnée à exporter'); return }
    const headers = ['ID', 'Date', 'SCI', 'Libellé', 'Catégorie', 'Montant', 'Statut']
    const rows = transactions.map((t) => [
      t.id,
      t.date,
      scis.find((s) => s.id === t.sci_id)?.nom ?? t.sci_id,
      `"${t.libelle.replace(/"/g, '""')}"`,
      t.categorie ?? '',
      t.montant,
      t.statut,
    ])
    const csv = [headers, ...rows].map((r) => r.join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `transactions_page${page}.csv`
    a.click()
    URL.revokeObjectURL(url)
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
            <button
              onClick={() => validate.mutate(t.id, { onSuccess: () => toast.success('Transaction validée'), onError: () => toast.error('Erreur validation') })}
              className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-[#22c55e] hover:bg-[#22c55e]/10 transition-colors" title="Valider"
            >
              <CheckCircle className="h-3 w-3" />
            </button>
            <button
              onClick={() => reject.mutate(t.id, { onSuccess: () => toast.success('Transaction rejetée'), onError: () => toast.error('Erreur rejet') })}
              className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-[#ef4444] hover:bg-[#ef4444]/10 transition-colors" title="Rejeter"
            >
              <XCircle className="h-3 w-3" />
            </button>
          </>
        )}
        <button
          onClick={() => openEdit(t)}
          className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-white hover:bg-[#262626] transition-colors" title="Modifier"
        >
          <Pencil className="h-3 w-3" />
        </button>
        <button
          onClick={() => setConfirmDelete(t)}
          className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-[#ef4444] hover:bg-[#ef4444]/10 transition-colors" title="Supprimer"
        >
          <Trash2 className="h-3 w-3" />
        </button>
      </div>
    )},
  ]

  const revenus = transactions.filter((t) => t.montant > 0).reduce((s, t) => s + t.montant, 0)
  const depenses = transactions.filter((t) => t.montant < 0).reduce((s, t) => s + t.montant, 0)
  const net = revenus + depenses

  const inputCls = 'w-full h-7 text-xs bg-[#0d0d0d] border border-[#262626] rounded px-2 text-white focus:outline-none focus:border-[#404040]'
  const labelCls = 'block text-[10px] text-[#525252] uppercase tracking-wide mb-1'

  return (
    <div className="space-y-3">
      {/* Header + filters */}
      <div className="flex items-center gap-2 flex-wrap">
        <h2 className="text-xs font-semibold text-white uppercase tracking-wider">Transactions</h2>
        <div className="flex items-center gap-2 ml-auto">
          {[
            { value: sciFilter, onChange: setSciFilter, options: [{ label: 'Toutes SCI', value: '' }, ...scis.map((s) => ({ label: s.nom, value: String(s.id) }))] },
            { value: catFilter, onChange: setCatFilter, options: [{ label: 'Toutes catégories', value: '' }, ...CATEGORIES.map((c) => ({ label: c.label, value: c.value }))] },
            { value: statutFilter, onChange: setStatutFilter, options: [{ label: 'Tous statuts', value: '' }, { label: 'Validé', value: 'valide' }, { label: 'En attente', value: 'en_attente' }, { label: 'Rejeté', value: 'rejete' }] },
          ].map((sel, i) => (
            <select key={i} value={sel.value} onChange={(e) => sel.onChange(e.target.value)}
              className="h-7 text-xs bg-[#0d0d0d] border border-[#262626] rounded px-2 text-[#a3a3a3] focus:outline-none"
            >
              {sel.options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
          ))}
          <button onClick={exportCSV} className="flex items-center gap-1 h-7 px-2 bg-[#262626] text-[#a3a3a3] text-xs rounded hover:bg-[#404040] transition-colors">
            <Download className="h-3 w-3" />CSV
          </button>
          <button onClick={() => setShowCreate(true)} className="flex items-center gap-1.5 h-7 px-3 bg-white text-black text-xs font-medium rounded hover:bg-[#e5e5e5] transition-colors">
            <Plus className="h-3 w-3" />Ajouter
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-[#111111] border border-[#262626] rounded-md p-3">
        <DataTable
          columns={columns} data={transactions} loading={isLoading}
          emptyMessage="Aucune transaction" rowKey={(r) => r.id}
          pagination={data ? { page, totalPages: data.pages, total: data.total, onPageChange: setPage } : undefined}
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

      {/* Modal Éditer */}
      {editingTx && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <div className="bg-[#111111] border border-[#262626] rounded-lg p-5 w-96 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-semibold text-white uppercase tracking-wider">Modifier transaction #{editingTx.id}</h3>
              <button onClick={() => setEditingTx(null)} className="text-[#525252] hover:text-white"><X className="h-4 w-4" /></button>
            </div>
            <div className="space-y-3">
              <div>
                <label className={labelCls}>Date</label>
                <input type="date" value={editForm.date} onChange={(e) => setEditForm((f) => ({ ...f, date: e.target.value }))} className={inputCls} />
              </div>
              <div>
                <label className={labelCls}>Montant (€)</label>
                <input type="number" step="0.01" value={editForm.montant} onChange={(e) => setEditForm((f) => ({ ...f, montant: e.target.value }))} className={inputCls} />
              </div>
              <div>
                <label className={labelCls}>Libellé</label>
                <input type="text" value={editForm.libelle} onChange={(e) => setEditForm((f) => ({ ...f, libelle: e.target.value }))} className={inputCls} />
              </div>
              <div>
                <label className={labelCls}>Catégorie</label>
                <select value={editForm.categorie} onChange={(e) => setEditForm((f) => ({ ...f, categorie: e.target.value }))} className={inputCls}>
                  <option value="">— Sélectionner —</option>
                  {CATEGORIES.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
                </select>
              </div>
            </div>
            <div className="flex gap-2 pt-1">
              <button onClick={() => setEditingTx(null)} className="flex-1 h-7 text-xs border border-[#262626] text-[#a3a3a3] rounded hover:bg-[#1a1a1a] transition-colors">Annuler</button>
              <button onClick={submitEdit} disabled={updateTx.isPending} className="flex-1 h-7 text-xs bg-white text-black rounded hover:bg-[#e5e5e5] transition-colors disabled:opacity-50">
                {updateTx.isPending ? '…' : 'Enregistrer'}
              </button>
            </div>
          </div>
        </div>
      )}

      {confirmDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <div className="bg-[#111111] border border-[#262626] rounded-lg p-5 w-96 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-semibold text-white uppercase tracking-wider">Supprimer transaction #{confirmDelete.id}</h3>
              <button onClick={() => setConfirmDelete(null)} className="text-[#525252] hover:text-white"><X className="h-4 w-4" /></button>
            </div>
            <p className="text-sm text-[#a3a3a3]">
              Supprimer <span className="text-white font-semibold">{confirmDelete.libelle}</span> ({formatCurrency(confirmDelete.montant)}) ?
            </p>
            <div className="flex gap-2 pt-1">
              <button onClick={() => setConfirmDelete(null)} className="flex-1 h-7 text-xs border border-[#262626] text-[#a3a3a3] rounded hover:bg-[#1a1a1a] transition-colors">Annuler</button>
              <button
                onClick={() => deleteTx.mutate(confirmDelete.id, {
                  onSuccess: () => { toast.success('Transaction supprimée'); setConfirmDelete(null) },
                  onError: () => toast.error('Erreur lors de la suppression'),
                })}
                disabled={deleteTx.isPending}
                className="flex-1 h-7 text-xs bg-[#ef4444] text-white rounded hover:bg-[#dc2626] transition-colors disabled:opacity-50"
              >
                {deleteTx.isPending ? '…' : 'Supprimer'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Créer */}
      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <div className="bg-[#111111] border border-[#262626] rounded-lg p-5 w-96 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-semibold text-white uppercase tracking-wider">Nouvelle transaction</h3>
              <button onClick={() => setShowCreate(false)} className="text-[#525252] hover:text-white"><X className="h-4 w-4" /></button>
            </div>
            <div className="space-y-3">
              <div>
                <label className={labelCls}>SCI *</label>
                <select value={createForm.sci_id} onChange={(e) => setCreateForm((f) => ({ ...f, sci_id: e.target.value }))} className={inputCls}>
                  <option value="">— Sélectionner —</option>
                  {scis.map((s) => <option key={s.id} value={s.id}>{s.nom}</option>)}
                </select>
              </div>
              <div>
                <label className={labelCls}>Date *</label>
                <input type="date" value={createForm.date} onChange={(e) => setCreateForm((f) => ({ ...f, date: e.target.value }))} className={inputCls} />
              </div>
              <div>
                <label className={labelCls}>Montant (€) *</label>
                <input type="number" step="0.01" placeholder="Ex: -1200.00" value={createForm.montant} onChange={(e) => setCreateForm((f) => ({ ...f, montant: e.target.value }))} className={inputCls} />
              </div>
              <div>
                <label className={labelCls}>Libellé *</label>
                <input type="text" placeholder="Description de la transaction" value={createForm.libelle} onChange={(e) => setCreateForm((f) => ({ ...f, libelle: e.target.value }))} className={inputCls} />
              </div>
              <div>
                <label className={labelCls}>Compte bancaire *</label>
                <input type="text" placeholder="Ex: FR76..." value={createForm.compte_bancaire_id} onChange={(e) => setCreateForm((f) => ({ ...f, compte_bancaire_id: e.target.value }))} className={inputCls} />
              </div>
              <div>
                <label className={labelCls}>Catégorie</label>
                <select value={createForm.categorie} onChange={(e) => setCreateForm((f) => ({ ...f, categorie: e.target.value }))} className={inputCls}>
                  <option value="">— Sélectionner —</option>
                  {CATEGORIES.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
                </select>
              </div>
            </div>
            <div className="flex gap-2 pt-1">
              <button onClick={() => setShowCreate(false)} className="flex-1 h-7 text-xs border border-[#262626] text-[#a3a3a3] rounded hover:bg-[#1a1a1a] transition-colors">Annuler</button>
              <button onClick={submitCreate} disabled={createTx.isPending} className="flex-1 h-7 text-xs bg-white text-black rounded hover:bg-[#e5e5e5] transition-colors disabled:opacity-50">
                {createTx.isPending ? '…' : 'Créer'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
