import Link from 'next/link'
import { formatCurrency, formatPercentRaw } from '@/lib/utils/format'
import { useDashboardOpportunites } from '@/lib/hooks/useDashboard'
import type { Opportunite } from '@/lib/types'

function scoreStyle(score: number): { bg: string; text: string; border: string } {
  if (score >= 85) return { bg: 'bg-[#22c55e]/20', text: 'text-[#22c55e]', border: 'border-[#22c55e]/30' }
  if (score >= 70) return { bg: 'bg-[#eab308]/20', text: 'text-[#eab308]', border: 'border-[#eab308]/30' }
  return { bg: 'bg-[#ef4444]/20', text: 'text-[#ef4444]', border: 'border-[#ef4444]/30' }
}

function dpeColor(dpe?: string): string {
  const map: Record<string, string> = { A: '#22c55e', B: '#84cc16', C: '#eab308', D: '#f97316', E: '#ef4444', F: '#dc2626', G: '#991b1b' }
  return map[dpe ?? ''] ?? '#737373'
}

export default function OpportunitesWidget() {
  const { data: opportunites = [], isLoading } = useDashboardOpportunites(2)

  return (
    <div className="h-48 p-2 bg-[#111111] border border-[#262626] rounded-md flex flex-col">
      <div className="flex items-center justify-between mb-2">
        <span className="text-[10px] text-[#737373] uppercase tracking-wide">Opportunités IA</span>
        <span className="bg-[#22c55e]/20 text-[#22c55e] border border-[#22c55e]/30 rounded-full px-1.5 py-0.5 text-[9px] font-medium">
          {isLoading ? '…' : `${opportunites.length} top`}
        </span>
      </div>
      <div className="space-y-1.5 flex-1">
        {isLoading ? (
          Array.from({ length: 2 }).map((_, i) => (
            <div key={i} className="h-12 bg-[#262626]/30 rounded animate-pulse" />
          ))
        ) : opportunites.length === 0 ? (
          <p className="text-[10px] text-[#525252] text-center pt-4">Aucune opportunité</p>
        ) : (
          opportunites.map((opp: Opportunite) => {
            const s = scoreStyle(opp.score)
            return (
              <div
                key={opp.id}
                className="bg-[#0d0d0d] border border-[#262626] rounded p-1.5 flex items-center gap-2"
              >
                <div className={`w-9 h-9 rounded-full flex-shrink-0 flex items-center justify-center border ${s.bg} ${s.border}`}>
                  <span className={`text-[10px] font-mono font-semibold ${s.text}`}>{opp.score}</span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-[10px] text-white truncate leading-tight">{opp.adresse}</p>
                  <p className="text-[9px] text-[#525252]">{opp.ville}</p>
                  <div className="flex items-center gap-1.5 mt-0.5">
                    <span className="font-mono text-[9px] text-white">{formatCurrency(opp.prix)}</span>
                    {opp.tri_estime && (
                      <span className="text-[#22c55e] text-[9px] font-mono">{formatPercentRaw(opp.tri_estime)}</span>
                    )}
                    {opp.dpe && (
                      <span
                        className="text-[8px] font-bold px-1 rounded"
                        style={{ color: dpeColor(opp.dpe), background: `${dpeColor(opp.dpe)}22` }}
                      >
                        DPE {opp.dpe}
                      </span>
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
        className="text-[9px] text-[#525252] hover:text-white transition-colors pt-1.5 text-right block"
      >
        Voir toutes →
      </Link>
    </div>
  )
}
