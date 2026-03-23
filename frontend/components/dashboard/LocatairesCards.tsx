import { formatCurrency } from '@/lib/utils/format'
import { cn } from '@/lib/utils/cn'

interface LocataireItem {
  id: number
  nom: string
  bien: string
  loyer: number
  statut: 'a_jour' | 'retard' | 'impaye'
  jours_retard?: number
}

const MOCK: LocataireItem[] = [
  { id: 1, nom: 'Karim Benzara', bien: '12 Rue du Commerce', loyer: 1_450, statut: 'a_jour' },
  { id: 2, nom: 'Sophie Durand', bien: '7 Av. Jean Jaurès', loyer: 1_100, statut: 'retard', jours_retard: 8 },
]

function StatusDot({ statut, jours_retard }: { statut: LocataireItem['statut']; jours_retard?: number }) {
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
  return (
    <div className="h-48 p-2 bg-[#111111] border border-[#262626] rounded-md flex flex-col">
      <div className="flex items-center justify-between mb-2">
        <span className="text-[10px] text-[#737373] uppercase tracking-wide">Locataires</span>
        <span className="text-[9px] bg-[#262626] text-[#a3a3a3] rounded-full px-1.5 py-0.5">
          {MOCK.length}
        </span>
      </div>
      <div className="flex-1 overflow-y-auto space-y-1.5 min-h-0">
        {MOCK.map((loc) => (
          <div
            key={loc.id}
            className="bg-[#0d0d0d] border border-[#262626] rounded p-2"
          >
            <div className="flex items-start justify-between gap-1">
              <div className="min-w-0 flex-1">
                <p className="text-xs text-white truncate leading-tight">{loc.nom}</p>
                <p className="text-[9px] text-[#525252] truncate mt-0.5">{loc.bien}</p>
              </div>
              <span className="font-mono text-[10px] text-white flex-shrink-0 tabular-nums">
                {formatCurrency(loc.loyer)}/m
              </span>
            </div>
            <div className="mt-1">
              <StatusDot statut={loc.statut} jours_retard={loc.jours_retard} />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
