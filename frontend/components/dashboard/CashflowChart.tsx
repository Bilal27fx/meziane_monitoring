'use client'

import { AreaChart, Area, XAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { formatCurrency } from '@/lib/utils/format'

interface DataPoint {
  date: string
  value: number
}

interface CashflowChartProps {
  data?: DataPoint[]
}


function formatLabel(dateStr: string) {
  const d = new Date(dateStr)
  return `${d.getDate()}`
}

interface TooltipPayload {
  value: number
}

function CustomTooltip({ active, payload, label }: { active?: boolean; payload?: TooltipPayload[]; label?: string }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-[#111111] border border-[#262626] rounded px-2 py-1.5">
      <p className="text-[9px] text-[#525252] mb-0.5">{label}</p>
      <p className="text-[10px] font-mono text-[#22c55e]">{formatCurrency(payload[0].value)}</p>
    </div>
  )
}

export default function CashflowChart({ data = [] }: CashflowChartProps) {
  const ticks = data.filter((_, i) => i % 5 === 0).map((d) => d.date)

  return (
    <div className="h-48 p-2 bg-[#111111] border border-[#262626] rounded-md flex flex-col">
      <div className="flex items-center justify-between mb-1">
        <span className="text-[10px] text-[#737373] uppercase tracking-wide">Cashflow 30j</span>
        <span className="text-[10px] font-mono text-[#22c55e]">
          {formatCurrency(data[data.length - 1]?.value ?? 0)}
        </span>
      </div>
      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%" minWidth={0} debounce={50}>
          <AreaChart data={data} margin={{ top: 4, right: 0, bottom: 0, left: 0 }}>
            <defs>
              <linearGradient id="cashflowGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#22c55e" stopOpacity={0.15} />
                <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" vertical={false} />
            <XAxis
              dataKey="date"
              ticks={ticks}
              tickFormatter={formatLabel}
              tick={{ fontSize: 8, fill: '#525252' }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="value"
              stroke="#22c55e"
              strokeWidth={1.5}
              fill="url(#cashflowGrad)"
              dot={false}
              activeDot={{ r: 3, fill: '#22c55e', stroke: '#111111', strokeWidth: 1 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
