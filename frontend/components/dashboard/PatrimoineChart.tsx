'use client'

import { LineChart, Line, XAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { formatCurrency } from '@/lib/utils/format'

interface DataPoint {
  date: string
  value: number
}

interface PatrimoineChartProps {
  data?: DataPoint[]
}

const MONTHS = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']


function formatLabel(dateStr: string) {
  const d = new Date(dateStr)
  return MONTHS[d.getMonth()]
}

interface TooltipPayload {
  value: number
}

function CustomTooltip({ active, payload, label }: { active?: boolean; payload?: TooltipPayload[]; label?: string }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-[#111111] border border-[#262626] rounded px-2 py-1.5">
      <p className="text-[9px] text-[#525252] mb-0.5">{label}</p>
      <p className="text-[10px] font-mono text-[#3b82f6]">{formatCurrency(payload[0].value)}</p>
    </div>
  )
}

export default function PatrimoineChart({ data = [] }: PatrimoineChartProps) {
  return (
    <div className="h-48 p-2 bg-[#111111] border border-[#262626] rounded-md flex flex-col">
      <div className="flex items-center justify-between mb-1">
        <span className="text-[10px] text-[#737373] uppercase tracking-wide">Patrimoine net</span>
        <span className="text-[10px] font-mono text-[#3b82f6]">
          {formatCurrency(data[data.length - 1]?.value ?? 0)}
        </span>
      </div>
      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%" minWidth={0} debounce={50}>
          <LineChart data={data} margin={{ top: 4, right: 0, bottom: 0, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" vertical={false} />
            <XAxis
              dataKey="date"
              tickFormatter={formatLabel}
              tick={{ fontSize: 8, fill: '#525252' }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip content={<CustomTooltip />} />
            <Line
              type="monotone"
              dataKey="value"
              stroke="#3b82f6"
              strokeWidth={1.5}
              dot={false}
              activeDot={{ r: 3, fill: '#3b82f6', stroke: '#111111', strokeWidth: 1 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
