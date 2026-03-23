import { formatCurrency } from '@/lib/utils/format'
import type { SCIOverviewItem } from '@/lib/types'

interface SCIOverviewProps {
  data?: SCIOverviewItem[]
}

const DEFAULT_DATA: SCIOverviewItem[] = [
  { id: 1, nom: 'SCI Facha', cashflow_mensuel: 2_150, nb_biens: 3, valeur_totale: 910_000 },
  { id: 2, nom: 'La Renaissance', cashflow_mensuel: 1_320, nb_biens: 2, valeur_totale: 685_000 },
  { id: 3, nom: 'Patrimoine+', cashflow_mensuel: 745, nb_biens: 2, valeur_totale: 792_500 },
]

export default function SCIOverview({ data = DEFAULT_DATA }: SCIOverviewProps) {
  return (
    <div className="h-48 p-2 bg-[#111111] border border-[#262626] rounded-md flex flex-col">
      <div className="flex items-center justify-between mb-2">
        <span className="text-[10px] text-[#737373] uppercase tracking-wide">SCI Overview</span>
        <span className="text-[9px] bg-[#262626] text-[#a3a3a3] rounded-full px-1.5 py-0.5">
          {data.length}
        </span>
      </div>
      <div className="grid grid-cols-3 gap-1.5 flex-1">
        {data.map((sci) => (
          <div
            key={sci.id}
            className="bg-[#0d0d0d] border border-[#262626] rounded p-1.5 flex flex-col gap-0.5"
          >
            <span className="text-[10px] text-[#a3a3a3] truncate leading-tight">{sci.nom}</span>
            <span className="text-xs font-mono text-[#22c55e] leading-tight">
              +{formatCurrency(sci.cashflow_mensuel)}/m
            </span>
            <span className="text-[9px] text-[#525252]">
              {sci.nb_biens} bien{sci.nb_biens !== 1 ? 's' : ''}
            </span>
            <span className="text-[9px] font-mono text-[#737373]">
              {formatCurrency(sci.valeur_totale)}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
