import Link from 'next/link'
import { formatCurrency, formatPercentRaw } from '@/lib/utils/format'
import type { OpportuniteOverview } from '@/lib/types'

interface OpportunitesWidgetProps {
  data?: OpportuniteOverview[]
  isLoading?: boolean
}

function scoreStyle(score: number): { bg: string; text: string; border: string } {
  if (score >= 85) return { bg: 'bg-[#22c55e]/20', text: 'text-[#22c55e]', border: 'border-[#22c55e]/30' }
  if (score >= 70) return { bg: 'bg-[#eab308]/20', text: 'text-[#eab308]', border: 'border-[#eab308]/30' }
  return { bg: 'bg-[#ef4444]/20', text: 'text-[#ef4444]', border: 'border-[#ef4444]/30' }
}

export default function OpportunitesWidget({ data = [], isLoading = false }: OpportunitesWidgetProps) {
  const opportunites = data.slice(0, 2)

  return (
    <div className="p-3.5 bg-[#111111] border border-[#262626] rounded-lg flex flex-col hover:border-[#404040] transition-colors">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs text-[#a3a3a3] uppercase tracking-widest font-medium">Opportunités IA</span>
        <span className="bg-[#22c55e]/20 text-[#22c55e] border border-[#22c55e]/30 rounded-full px-2 py-0.5 text-xs font-semibold">
          {isLoading ? '…' : `${opportunites.length} top`}
        </span>
      </div>
      <div className="space-y-2 flex-1">
        {isLoading ? (
          Array.from({ length: 2 }).map((_, i) => (
            <div key={i} className="h-14 bg-[#262626]/30 rounded-md animate-pulse" />
          ))
        ) : opportunites.length === 0 ? (
          <p className="text-xs text-[#737373] text-center pt-4">Aucune opportunité</p>
        ) : (
          opportunites.map((opp: OpportuniteOverview) => {
            const score = opp.score_global ?? 0
            const s = scoreStyle(score)
            return (
              <div
                key={opp.id}
                className="bg-[#0d0d0d] border border-[#262626] rounded-md p-2.5 flex items-center gap-3 hover:border-[#404040] transition-colors"
              >
                <div className={`w-10 h-10 rounded-full flex-shrink-0 flex items-center justify-center border ${s.bg} ${s.border}`}>
                  <span className={`text-xs font-mono font-bold ${s.text}`}>{score}</span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white truncate leading-tight font-medium">
                    {opp.titre ?? opp.ville}
                  </p>
                  <p className="text-xs text-[#737373] mt-0.5">{opp.ville}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="font-mono text-xs text-[#d4d4d4] font-semibold">{formatCurrency(opp.prix)}</span>
                    {opp.rentabilite_nette != null && (
                      <span className="text-[#22c55e] text-xs font-mono font-semibold">{formatPercentRaw(opp.rentabilite_nette)}</span>
                    )}
                    {opp.surface && (
                      <span className="text-xs text-[#737373]">{opp.surface}m²</span>
                    )}
                  </div>
                </div>
              </div>
            )
          })
        )}
      </div>
      <Link
        href="/agent"
        className="text-xs text-[#737373] hover:text-white transition-colors pt-2.5 text-right block font-medium"
      >
        Voir toutes →
      </Link>
    </div>
  )
}
