import { formatCurrency } from '@/lib/utils/format'
import type { SCIOverviewItem } from '@/lib/types'

interface SCIOverviewProps {
  data?: SCIOverviewItem[]
}

export default function SCIOverview({ data = [] }: SCIOverviewProps) {
  return (
    <div className="h-56 p-3.5 bg-[#111111] border border-[#262626] rounded-lg flex flex-col hover:border-[#404040] transition-colors">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs text-[#a3a3a3] uppercase tracking-widest font-medium">SCI Overview</span>
        <span className="text-xs bg-[#262626] text-[#d4d4d4] rounded-full px-2 py-0.5 font-medium">
          {data.length}
        </span>
      </div>
      <div className="grid grid-cols-3 gap-2 flex-1">
        {data.map((sci) => (
          <div
            key={sci.id}
            className="bg-[#0d0d0d] border border-[#262626] rounded-md p-2 flex flex-col gap-1 hover:border-[#404040] transition-colors"
          >
            <span className="text-xs text-[#d4d4d4] truncate leading-tight font-medium">{sci.nom}</span>
            <span className="text-sm font-mono text-[#22c55e] leading-tight font-semibold">
              {formatCurrency(sci.cashflow_annuel)}/an
            </span>
            <span className="text-xs text-[#737373]">
              {sci.nb_biens} bien{sci.nb_biens !== 1 ? 's' : ''}
            </span>
            <span className="text-xs font-mono text-[#a3a3a3]">
              {formatCurrency(sci.valeur_patrimoniale)}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
