import { formatCurrency } from '@/lib/utils/format'
import { useDashboardLocataires } from '@/lib/hooks/useDashboard'
import type { Locataire } from '@/lib/types'

function StatusDot({ statut, jours_retard }: { statut: Locataire['statut_paiement']; jours_retard?: number }) {
  if (statut === 'a_jour') {
    return (
      <div className="flex items-center gap-1">
        <span className="w-1.5 h-1.5 rounded-full bg-[#22c55e] flex-shrink-0" />
        <span className="text-[9px] text-[#737373]">À jour</span>
      </div>
    )
  }
  if (statut === 'retard') {
    return (
      <div className="flex items-center gap-1">
        <span className="w-1.5 h-1.5 rounded-full bg-[#eab308] flex-shrink-0" />
        <span className="text-[9px] text-[#eab308]">Retard J+{jours_retard}</span>
      </div>
    )
  }
  return (
    <div className="flex items-center gap-1">
      <span className="w-1.5 h-1.5 rounded-full bg-[#ef4444] animate-pulse flex-shrink-0" />
      <span className="text-[9px] text-[#ef4444] font-semibold">Impayé</span>
    </div>
  )
}

export default function LocatairesCards() {
  const { data: locataires = [], isLoading } = useDashboardLocataires()

  return (
    <div className="h-48 p-2 bg-[#111111] border border-[#262626] rounded-md flex flex-col">
      <div className="flex items-center justify-between mb-2">
        <span className="text-[10px] text-[#737373] uppercase tracking-wide">Locataires</span>
        <span className="text-[9px] bg-[#262626] text-[#a3a3a3] rounded-full px-1.5 py-0.5">
          {isLoading ? '…' : locataires.length}
        </span>
      </div>
      <div className="flex-1 overflow-y-auto space-y-1.5 min-h-0">
        {isLoading ? (
          Array.from({ length: 2 }).map((_, i) => (
            <div key={i} className="h-12 bg-[#262626]/30 rounded animate-pulse" />
          ))
        ) : locataires.length === 0 ? (
          <p className="text-[10px] text-[#525252] text-center pt-4">Aucun locataire</p>
        ) : (
          locataires.map((loc: Locataire) => (
            <div key={loc.id} className="bg-[#0d0d0d] border border-[#262626] rounded p-2">
              <div className="flex items-start justify-between gap-1">
                <div className="min-w-0 flex-1">
                  <p className="text-xs text-white truncate leading-tight">{loc.prenom} {loc.nom}</p>
                  <p className="text-[9px] text-[#525252] truncate mt-0.5">{loc.bail?.bien_adresse ?? '—'}</p>
                </div>
                <span className="font-mono text-[10px] text-white flex-shrink-0 tabular-nums">
                  {loc.bail ? formatCurrency(loc.bail.loyer_mensuel) : '—'}/m
                </span>
              </div>
              <div className="mt-1">
                <StatusDot statut={loc.statut_paiement} jours_retard={loc.jours_retard} />
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
