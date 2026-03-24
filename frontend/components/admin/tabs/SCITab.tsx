'use client'

import { useState } from 'react'
import { Pencil, Trash2, Plus, FolderOpen } from 'lucide-react'
import { useSCIs, useDeleteSCI } from '@/lib/hooks/useAdmin'
import DataTable, { Column } from '@/components/ui/DataTable'
import Modal from '@/components/ui/Modal'
import SCIForm from '@/components/admin/forms/SCIForm'
import DocumentsPanel from '@/components/admin/panels/DocumentsPanel'
import { formatCurrency } from '@/lib/utils/format'
import toast from 'react-hot-toast'
import type { SCI } from '@/lib/types'

export default function SCITab() {
  const { data, isLoading } = useSCIs()
  const deleteSCI = useDeleteSCI()
  const scis = data?.items ?? []

  const [modalOpen, setModalOpen] = useState(false)
  const [editingSCI, setEditingSCI] = useState<SCI | undefined>()
  const [confirmDelete, setConfirmDelete] = useState<SCI | null>(null)
  const [docsOpen, setDocsOpen] = useState(false)
  const [selectedSCI, setSelectedSCI] = useState<SCI | null>(null)

  const handleEdit = (sci: SCI) => {
    setEditingSCI(sci)
    setModalOpen(true)
  }

  const handleCreate = () => {
    setEditingSCI(undefined)
    setModalOpen(true)
  }

  const handleDelete = async (sci: SCI) => {
    try {
      await deleteSCI.mutateAsync(sci.id)
      toast.success(`SCI "${sci.nom}" supprimée`)
      setConfirmDelete(null)
    } catch {
      toast.error('Erreur lors de la suppression')
    }
  }

  const columns: Column<SCI>[] = [
    { header: 'Nom', accessor: 'nom', render: (s) => <span className="text-xs font-semibold text-white">{s.nom}</span> },
    { header: 'SIRET', accessor: 'siret', render: (s) => <span className="font-mono text-xs text-[#a3a3a3]">{s.siret ?? '—'}</span> },
    { header: 'Nb biens', accessor: 'nb_biens', render: (s) => <span className="font-mono text-xs text-white">{s.nb_biens ?? 0}</span> },
    { header: 'Valeur', accessor: 'valeur_totale', render: (s) => <span className="font-mono text-xs text-white tabular-nums">{s.valeur_totale ? formatCurrency(s.valeur_totale) : '—'}</span> },
    {
      header: 'Cashflow/mois',
      accessor: 'cashflow_mensuel',
      render: (s) => (
        <span className={`font-mono text-xs tabular-nums ${(s.cashflow_mensuel ?? 0) >= 0 ? 'text-[#22c55e]' : 'text-[#ef4444]'}`}>
          {s.cashflow_mensuel !== undefined ? `${s.cashflow_mensuel >= 0 ? '+' : ''}${formatCurrency(s.cashflow_mensuel)}/m` : '—'}
        </span>
      ),
    },
    {
      header: 'Actions',
      accessor: 'id',
      render: (s) => (
        <div className="flex items-center gap-1">
          <button
            onClick={() => handleEdit(s)}
            className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-white hover:bg-[#262626] transition-colors"
          >
            <Pencil className="h-3 w-3" />
          </button>
          <button
            onClick={() => { setSelectedSCI(s); setDocsOpen(true) }}
            className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-[#3b82f6] hover:bg-[#3b82f6]/10 transition-colors"
            title="Documents"
          >
            <FolderOpen className="h-3 w-3" />
          </button>
          <button
            onClick={() => setConfirmDelete(s)}
            className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-[#ef4444] hover:bg-[#ef4444]/10 transition-colors"
          >
            <Trash2 className="h-3 w-3" />
          </button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-xs font-semibold text-white uppercase tracking-wider">Gestion SCI</h2>
        <button
          onClick={handleCreate}
          className="flex items-center gap-1.5 h-7 px-3 bg-white text-black text-xs font-medium rounded hover:bg-[#e5e5e5] transition-colors"
        >
          <Plus className="h-3 w-3" />
          Créer une SCI
        </button>
      </div>

      {/* Table */}
      <div className="bg-[#111111] border border-[#262626] rounded-md p-3">
        <DataTable
          columns={columns}
          data={scis}
          loading={isLoading}
          emptyMessage="Aucune SCI créée"
          rowKey={(r) => r.id}
        />
      </div>

      {/* Create/Edit Modal */}
      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editingSCI ? `Modifier — ${editingSCI.nom}` : 'Créer une SCI'}
      >
        <SCIForm sci={editingSCI} onClose={() => setModalOpen(false)} />
      </Modal>

      {/* Documents Panel */}
      <DocumentsPanel
        open={docsOpen}
        onClose={() => setDocsOpen(false)}
        entityType="sci"
        entityId={selectedSCI?.id ?? null}
        entityNom={selectedSCI?.nom}
      />

      {/* Confirm Delete Modal */}
      <Modal
        open={confirmDelete !== null}
        onClose={() => setConfirmDelete(null)}
        title="Confirmer la suppression"
        size="sm"
      >
        <p className="text-sm text-[#a3a3a3] mb-4">
          Supprimer la SCI <span className="text-white font-semibold">{confirmDelete?.nom}</span> ? Cette action est irréversible.
        </p>
        <div className="flex gap-2">
          <button
            onClick={() => setConfirmDelete(null)}
            className="flex-1 h-8 text-xs text-[#737373] bg-[#1a1a1a] hover:bg-[#262626] rounded transition-colors"
          >
            Annuler
          </button>
          <button
            onClick={() => confirmDelete && handleDelete(confirmDelete)}
            disabled={deleteSCI.isPending}
            className="flex-1 h-8 text-xs text-white bg-[#ef4444] hover:bg-[#dc2626] rounded transition-colors disabled:opacity-50"
          >
            Supprimer
          </button>
        </div>
      </Modal>
    </div>
  )
}
