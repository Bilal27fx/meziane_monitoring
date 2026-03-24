import { cn } from '@/lib/utils/cn'
import { formatCurrency, formatPercentRaw } from '@/lib/utils/format'
import type { TopBien } from '@/lib/types'

interface Top5BiensProps {
  data?: TopBien[]
}


function triColor(tri: number): string {
  if (tri >= 7) return '#22c55e'
  if (tri >= 4) return '#eab308'
  return '#ef4444'
}

const MAX_TRI = 10

export default function Top5Biens({ data = [] }: Top5BiensProps) {
  return (
    <div className="h-full p-3.5 bg-[#111111] border border-[#262626] rounded-lg flex flex-col hover:border-[#404040] transition-colors">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs text-[#a3a3a3] uppercase tracking-widest font-medium">Top Biens</span>
        <span className="text-xs text-[#737373] font-medium">TRI Net · YTD</span>
      </div>
      <div className="flex-1 overflow-y-auto space-y-2 min-h-0">
        {data.map((bien, idx) => {
          const color = triColor(bien.rentabilite_nette)
          const pct = Math.min((bien.rentabilite_nette / MAX_TRI) * 100, 100)
          return (
            <div
              key={bien.id}
              className="bg-[#0d0d0d] border border-[#262626] rounded-md p-2.5 hover:border-[#404040] transition-colors"
            >
              <div className="flex items-start gap-2.5">
                <span className="text-xs text-[#737373] font-mono w-4 flex-shrink-0 mt-0.5 font-semibold">
                  {idx + 1}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white truncate leading-tight font-medium">{bien.adresse}</p>
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-xs text-[#737373]">
                      {bien.ville} · {formatCurrency(bien.valeur_actuelle)}
                    </span>
                    <span
                      className="text-sm font-mono font-semibold flex-shrink-0 ml-2"
                      style={{ color }}
                    >
                      {formatPercentRaw(bien.rentabilite_nette)}
                    </span>
                  </div>
                  <div className="mt-2 bg-[#262626] h-1.5 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all"
                      style={{ width: `${pct}%`, backgroundColor: color }}
                    />
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
