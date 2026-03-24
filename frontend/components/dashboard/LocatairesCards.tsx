import { formatCurrency } from '@/lib/utils/format'
import { useDashboardLocataires } from '@/lib/hooks/useDashboard'
import type { LocataireOverview } from '@/lib/types'

function mapStatut(statut: string): 'a_jour' | 'retard' | 'impaye' {
  if (statut === 'paye') return 'a_jour'
  if (statut === 'impaye') return 'impaye'
  return 'retard' // partiel, en_attente
}

function StatusDot({ statut, nb_impayes }: { statut: string; nb_impayes: number }) {
  const mapped = mapStatut(statut)
  if (mapped === 'a_jour') {
    return (
      <div className="flex items-center gap-1.5">
        <span className="w-2 h-2 rounded-full bg-[#22c55e] flex-shrink-0" />
        <span className="text-xs text-[#a3a3a3]">À jour</span>
      </div>
    )
  }
  if (mapped === 'retard') {
    return (
      <div className="flex items-center gap-1.5">
        <span className="w-2 h-2 rounded-full bg-[#eab308] flex-shrink-0" />
        <span className="text-xs text-[#eab308] font-medium">{nb_impayes > 0 ? `${nb_impayes} impayé(s)` : 'Partiel'}</span>
      </div>
    )
  }
  return (
    <div className="flex items-center gap-1.5">
      <span className="w-2 h-2 rounded-full bg-[#ef4444] animate-pulse flex-shrink-0" />
      <span className="text-xs text-[#ef4444] font-semibold">Impayé</span>
    </div>
  )
}

export default function LocatairesCards() {
  const { data: locataires = [], isLoading } = useDashboardLocataires()

  return (
    <div className="p-3.5 bg-[#111111] border border-[#262626] rounded-lg flex flex-col hover:border-[#404040] transition-colors">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs text-[#a3a3a3] uppercase tracking-widest font-medium">Locataires</span>
        <span className="text-xs bg-[#262626] text-[#d4d4d4] rounded-full px-2 py-0.5 font-medium">
          {isLoading ? '…' : locataires.length}
        </span>
      </div>
      <div className="overflow-y-auto space-y-2 min-h-0 max-h-64">
        {isLoading ? (
          Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-14 bg-[#262626]/30 rounded-md animate-pulse" />
          ))
        ) : locataires.length === 0 ? (
          <p className="text-xs text-[#737373] text-center pt-4">Aucun locataire</p>
        ) : (
          locataires.map((loc: LocataireOverview) => (
            <div key={loc.id} className="bg-[#0d0d0d] border border-[#262626] rounded-md p-2.5 hover:border-[#404040] transition-colors">
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <p className="text-sm text-white truncate leading-tight font-medium">{loc.prenom} {loc.nom}</p>
                  <p className="text-xs text-[#737373] truncate mt-0.5">{loc.bien_adresse ?? '—'}</p>
                </div>
                <span className="font-mono text-sm text-[#d4d4d4] flex-shrink-0 tabular-nums font-semibold">
                  {formatCurrency(loc.loyer_mensuel)}/m
                </span>
              </div>
              <div className="mt-1.5">
                <StatusDot statut={loc.statut_paiement} nb_impayes={loc.nb_impayes} />
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
