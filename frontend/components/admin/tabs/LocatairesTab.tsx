'use client'

import { useState } from 'react'
import { Pencil, Trash2, Plus, ClipboardList, MessageSquare, FolderOpen, Wallet } from 'lucide-react'
import { useLocataires, useDeleteLocataire } from '@/lib/hooks/useAdmin'
import DataTable, { Column } from '@/components/ui/DataTable'
import Modal from '@/components/ui/Modal'
import LocataireForm from '@/components/admin/forms/LocataireForm'
import QuittancesPanel from '@/components/admin/panels/QuittancesPanel'
import DocumentsPanel from '@/components/admin/panels/DocumentsPanel'
import LocatairePaymentsPanel from '@/components/admin/panels/LocatairePaymentsPanel'
import Badge from '@/components/ui/Badge'
import { formatCurrency } from '@/lib/utils/format'
import toast from 'react-hot-toast'
import type { Locataire } from '@/lib/types'

export default function LocatairesTab() {
  const { data, isLoading } = useLocataires()
  const deleteLocataire = useDeleteLocataire()
  const locataires = data?.items ?? []

  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Locataire | undefined>()
  const [confirmDelete, setConfirmDelete] = useState<Locataire | null>(null)
  const [quittancesOpen, setQuittancesOpen] = useState(false)
  const [selectedLocataire, setSelectedLocataire] = useState<Locataire | null>(null)
  const [docsOpen, setDocsOpen] = useState(false)
  const [docsLocataire, setDocsLocataire] = useState<Locataire | null>(null)
  const [paymentsOpen, setPaymentsOpen] = useState(false)
  const [paymentsLocataire, setPaymentsLocataire] = useState<Locataire | null>(null)

  const paiementVariant = (statut?: string) => {
    if (statut === 'a_jour') return 'ok' as const
    if (statut === 'retard') return 'warning' as const
    return 'error' as const
  }

  const paiementLabel = (loc: Locataire) => {
    if (loc.statut_paiement === 'a_jour') return 'À jour'
    if (loc.statut_paiement === 'retard') return `Retard J+${loc.jours_retard ?? '?'}`
    return 'Impayé'
  }

  const columns: Column<Locataire>[] = [
    { header: 'Locataire', accessor: 'nom', render: (l) => (
      <div>
        <p className="text-xs text-white">{l.prenom} {l.nom}</p>
        <p className="text-[9px] text-[#525252]">{l.email}</p>
      </div>
    )},
    { header: 'Bien', accessor: 'bien_id', render: (l) => (
      <span className="text-xs text-[#a3a3a3]">{l.bail?.bien_adresse ?? (l.bien_id ? `Bien #${l.bien_id}` : '—')}</span>
    )},
    { header: 'Bail', accessor: 'bail', render: (l) => (
      <span className="text-[10px] font-mono text-[#737373]">
        {l.bail ? `${new Date(l.bail.date_debut).toLocaleDateString('fr-FR', { month: 'short', year: '2-digit' })} →` : '—'}
      </span>
    )},
    { header: 'Loyer', accessor: 'bail', render: (l) => (
      <span className="font-mono text-xs text-white tabular-nums">
        {l.bail
          ? formatCurrency((l.bail.loyer_mensuel ?? 0) + (l.bail.charges_mensuelles ?? 0)) + '/m'
          : '—'}
      </span>
    )},
    { header: 'Paiement', accessor: 'statut_paiement', render: (l) => (
      <Badge variant={paiementVariant(l.statut_paiement)} dot>
        {paiementLabel(l)}
      </Badge>
    )},
    { header: 'Actions', accessor: 'id', render: (l) => (
      <div className="flex items-center gap-1">
        <button onClick={() => { setEditing(l); setModalOpen(true) }} className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-white hover:bg-[#262626] transition-colors">
          <Pencil className="h-3 w-3" />
        </button>
        <button onClick={() => { setPaymentsLocataire(l); setPaymentsOpen(true) }} className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-[#22c55e] hover:bg-[#22c55e]/10 transition-colors" title="Paiements">
          <Wallet className="h-3 w-3" />
        </button>
        <button onClick={() => { setSelectedLocataire(l); setQuittancesOpen(true) }} className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-[#3b82f6] hover:bg-[#3b82f6]/10 transition-colors" title="Quittances">
          <ClipboardList className="h-3 w-3" />
        </button>
        <button onClick={() => { setDocsLocataire(l); setDocsOpen(true) }} className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-[#a855f7] hover:bg-[#a855f7]/10 transition-colors" title="Documents">
          <FolderOpen className="h-3 w-3" />
        </button>
        <button onClick={() => toast.success('Fonctionnalité communication à venir')} className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-[#eab308] hover:bg-[#eab308]/10 transition-colors" title="Communication">
          <MessageSquare className="h-3 w-3" />
        </button>
        <button onClick={() => setConfirmDelete(l)} className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-[#ef4444] hover:bg-[#ef4444]/10 transition-colors">
          <Trash2 className="h-3 w-3" />
        </button>
      </div>
    )},
  ]

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-xs font-semibold text-white uppercase tracking-wider">Gestion Locataires</h2>
        <button
          onClick={() => { setEditing(undefined); setModalOpen(true) }}
          className="flex items-center gap-1.5 h-7 px-3 bg-white text-black text-xs font-medium rounded hover:bg-[#e5e5e5] transition-colors"
        >
          <Plus className="h-3 w-3" />
          Ajouter
        </button>
      </div>

      <div className="bg-[#111111] border border-[#262626] rounded-md p-3">
        <DataTable
          columns={columns}
          data={locataires}
          loading={isLoading}
          emptyMessage="Aucun locataire enregistré"
          rowKey={(r) => r.id}
        />
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editing ? `Modifier — ${editing.prenom} ${editing.nom}` : 'Ajouter un locataire'} size="lg">
        <LocataireForm locataire={editing} onClose={() => setModalOpen(false)} />
      </Modal>

      <Modal open={confirmDelete !== null} onClose={() => setConfirmDelete(null)} title="Confirmer la suppression" size="sm">
        <p className="text-sm text-[#a3a3a3] mb-4">Supprimer <span className="text-white font-semibold">{confirmDelete?.prenom} {confirmDelete?.nom}</span> ?</p>
        <div className="flex gap-2">
          <button onClick={() => setConfirmDelete(null)} className="flex-1 h-8 text-xs text-[#737373] bg-[#1a1a1a] hover:bg-[#262626] rounded">Annuler</button>
          <button onClick={async () => { if (confirmDelete) { await deleteLocataire.mutateAsync(confirmDelete.id); setConfirmDelete(null); toast.success('Locataire supprimé') }}} className="flex-1 h-8 text-xs text-white bg-[#ef4444] hover:bg-[#dc2626] rounded">Supprimer</button>
        </div>
      </Modal>

      <QuittancesPanel
        open={quittancesOpen}
        onClose={() => setQuittancesOpen(false)}
        locataireNom={selectedLocataire ? `${selectedLocataire.prenom} ${selectedLocataire.nom}` : undefined}
        locataireId={selectedLocataire?.id ?? null}
      />

      <DocumentsPanel
        open={docsOpen}
        onClose={() => setDocsOpen(false)}
        entityType="locataire"
        entityId={docsLocataire?.id ?? null}
        entityNom={docsLocataire ? `${docsLocataire.prenom} ${docsLocataire.nom}` : undefined}
      />

      <LocatairePaymentsPanel
        open={paymentsOpen}
        onClose={() => setPaymentsOpen(false)}
        locataire={paymentsLocataire}
      />
    </div>
  )
}
