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
    <div className="h-full p-2 bg-[#111111] border border-[#262626] rounded-md flex flex-col">
      <div className="flex items-center justify-between mb-2">
        <span className="text-[10px] text-[#737373] uppercase tracking-wide">Top Biens</span>
        <span className="text-[9px] text-[#525252]">TRI Net · YTD</span>
      </div>
      <div className="flex-1 overflow-y-auto space-y-1.5 min-h-0">
        {data.map((bien) => {
          const color = triColor(bien.tri_net)
          const pct = Math.min((bien.tri_net / MAX_TRI) * 100, 100)
          return (
            <div
              key={bien.id}
              className="bg-[#0d0d0d] border border-[#262626] rounded p-2 hover:border-[#404040] transition-colors"
            >
              <div className="flex items-start gap-2">
                <span className="text-[10px] text-[#525252] font-mono w-4 flex-shrink-0 mt-0.5">
                  {bien.rank}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-white truncate leading-tight">{bien.adresse}</p>
                  <div className="flex items-center justify-between mt-0.5">
                    <span className="text-[9px] text-[#525252]">
                      {bien.sci_nom} · {formatCurrency(bien.valeur)}
                    </span>
                    <span
                      className="text-[10px] font-mono font-semibold flex-shrink-0 ml-2"
                      style={{ color }}
                    >
                      {formatPercentRaw(bien.tri_net)}
                    </span>
                  </div>
                  <div className="mt-1.5 bg-[#262626] h-1 rounded-full overflow-hidden">
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
