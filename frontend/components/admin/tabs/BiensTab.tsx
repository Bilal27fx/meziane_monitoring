'use client'

import { useState } from 'react'
import { Pencil, Trash2, Plus, FolderOpen } from 'lucide-react'
import { useBiens, useDeleteBien, useSCIs } from '@/lib/hooks/useAdmin'
import DataTable, { Column } from '@/components/ui/DataTable'
import Modal from '@/components/ui/Modal'
import BienForm from '@/components/admin/forms/BienForm'
import DocumentsPanel from '@/components/admin/panels/DocumentsPanel'
import Badge from '@/components/ui/Badge'
import { formatCurrency, formatPercentRaw } from '@/lib/utils/format'
import { cn } from '@/lib/utils/cn'
import toast from 'react-hot-toast'
import type { Bien } from '@/lib/types'

export default function BiensTab() {
  const [sciFilter, setSciFilter] = useState('')
  const [statutFilter, setstatutFilter] = useState('')
  const { data, isLoading } = useBiens({
    sci_id: sciFilter ? Number(sciFilter) : undefined,
    statut: statutFilter || undefined,
  })
  const { data: scisData } = useSCIs()
  const deleteBien = useDeleteBien()
  const biens = data?.items ?? []
  const scis = scisData?.items ?? []

  const [modalOpen, setModalOpen] = useState(false)
  const [editingBien, setEditingBien] = useState<Bien | undefined>()
  const [confirmDelete, setConfirmDelete] = useState<Bien | null>(null)
  const [docsOpen, setDocsOpen] = useState(false)
  const [selectedBien, setSelectedBien] = useState<Bien | null>(null)

  const statutVariant = (statut: string) => {
    const map: Record<string, 'ok' | 'error' | 'warning' | 'default'> = {
      loue: 'ok', vacant: 'warning', travaux: 'default', vente: 'default',
    }
    return map[statut] ?? 'default'
  }

  const triColor = (tri?: number) => {
    if (!tri) return 'text-[#525252]'
    if (tri >= 7) return 'text-[#22c55e]'
    if (tri >= 4) return 'text-[#eab308]'
    return 'text-[#ef4444]'
  }

  const columns: Column<Bien>[] = [
    { header: 'Adresse', accessor: 'adresse', render: (b) => (
      <div>
        <p className="text-xs text-white">{b.adresse}</p>
        <p className="text-[9px] text-[#525252]">{b.ville} {b.code_postal}</p>
      </div>
    )},
    { header: 'SCI', accessor: 'sci_id', render: (b) => (
      <span className="text-xs text-[#a3a3a3]">{b.sci_nom ?? scis.find((s) => s.id === b.sci_id)?.nom ?? '—'}</span>
    )},
    { header: 'Type', accessor: 'type_bien', render: (b) => (
      <span className="text-xs text-[#737373] capitalize">{b.type_bien?.replace('_', ' ')}</span>
    )},
    { header: 'Valeur', accessor: 'valeur_actuelle', render: (b) => (
      <span className="font-mono text-xs text-white tabular-nums">{b.valeur_actuelle ? formatCurrency(b.valeur_actuelle) : '—'}</span>
    )},
    { header: 'Loyer', accessor: 'loyer_mensuel', render: (b) => (
      <span className="font-mono text-xs text-white tabular-nums">{b.loyer_mensuel ? formatCurrency(b.loyer_mensuel) + '/m' : '—'}</span>
    )},
    { header: 'TRI Net', accessor: 'tri_net', render: (b) => (
      <span className={cn('font-mono text-xs tabular-nums font-semibold', triColor(b.tri_net))}>
        {b.tri_net ? formatPercentRaw(b.tri_net) : '—'}
      </span>
    )},
    { header: 'Statut', accessor: 'statut', render: (b) => (
      <Badge variant={statutVariant(b.statut)} dot>
        {b.statut.charAt(0).toUpperCase() + b.statut.slice(1)}
      </Badge>
    )},
    { header: 'Actions', accessor: 'id', render: (b) => (
      <div className="flex items-center gap-1">
        <button onClick={() => { setEditingBien(b); setModalOpen(true) }} className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-white hover:bg-[#262626] transition-colors">
          <Pencil className="h-3 w-3" />
        </button>
        <button onClick={() => { setSelectedBien(b); setDocsOpen(true) }} className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-[#3b82f6] hover:bg-[#3b82f6]/10 transition-colors" title="Documents">
          <FolderOpen className="h-3 w-3" />
        </button>
        <button onClick={() => setConfirmDelete(b)} className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-[#ef4444] hover:bg-[#ef4444]/10 transition-colors">
          <Trash2 className="h-3 w-3" />
        </button>
      </div>
    )},
  ]

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <h2 className="text-xs font-semibold text-white uppercase tracking-wider">Gestion Biens</h2>
        <div className="flex items-center gap-2 ml-auto">
          <select
            value={sciFilter}
            onChange={(e) => setSciFilter(e.target.value)}
            className="h-7 text-xs bg-[#0d0d0d] border border-[#262626] rounded px-2 text-[#a3a3a3] focus:outline-none"
          >
            <option value="">Toutes SCI</option>
            {scis.map((s) => <option key={s.id} value={s.id}>{s.nom}</option>)}
          </select>
          <select
            value={statutFilter}
            onChange={(e) => setstatutFilter(e.target.value)}
            className="h-7 text-xs bg-[#0d0d0d] border border-[#262626] rounded px-2 text-[#a3a3a3] focus:outline-none"
          >
            <option value="">Tous statuts</option>
            {['loue', 'vacant', 'travaux', 'vente'].map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
          <button
            onClick={() => { setEditingBien(undefined); setModalOpen(true) }}
            className="flex items-center gap-1.5 h-7 px-3 bg-white text-black text-xs font-medium rounded hover:bg-[#e5e5e5] transition-colors"
          >
            <Plus className="h-3 w-3" />
            Ajouter
          </button>
        </div>
      </div>

      <div className="bg-[#111111] border border-[#262626] rounded-md p-3">
        <DataTable
          columns={columns}
          data={biens}
          loading={isLoading}
          emptyMessage="Aucun bien dans le portefeuille"
          rowKey={(r) => r.id}
        />
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editingBien ? `Modifier — ${editingBien.adresse}` : 'Ajouter un bien'} size="lg">
        <BienForm bien={editingBien} onClose={() => setModalOpen(false)} />
      </Modal>

      <Modal open={confirmDelete !== null} onClose={() => setConfirmDelete(null)} title="Confirmer la suppression" size="sm">
        <p className="text-sm text-[#a3a3a3] mb-4">Supprimer le bien <span className="text-white font-semibold">{confirmDelete?.adresse}</span> ?</p>
        <div className="flex gap-2">
          <button onClick={() => setConfirmDelete(null)} className="flex-1 h-8 text-xs text-[#737373] bg-[#1a1a1a] hover:bg-[#262626] rounded">Annuler</button>
          <button onClick={async () => { if (confirmDelete) { await deleteBien.mutateAsync(confirmDelete.id); setConfirmDelete(null); toast.success('Bien supprimé') }}} className="flex-1 h-8 text-xs text-white bg-[#ef4444] hover:bg-[#dc2626] rounded">Supprimer</button>
        </div>
      </Modal>

      <DocumentsPanel
        open={docsOpen}
        onClose={() => setDocsOpen(false)}
        entityType="bien"
        entityId={selectedBien?.id ?? null}
        entityNom={selectedBien?.adresse}
        sciId={selectedBien?.sci_id}
      />
    </div>
  )
}
