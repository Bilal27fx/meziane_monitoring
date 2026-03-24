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
    <div className="bg-[#1a1a1a] border border-[#404040] rounded-md px-3 py-2 shadow-lg">
      <p className="text-xs text-[#a3a3a3] mb-1">{label}</p>
      <p className="text-sm font-mono font-semibold text-[#3b82f6]">{formatCurrency(payload[0].value)}</p>
    </div>
  )
}

export default function PatrimoineChart({ data = [] }: PatrimoineChartProps) {
  return (
    <div className="h-56 p-3.5 bg-[#111111] border border-[#262626] rounded-lg flex flex-col hover:border-[#404040] transition-colors">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs text-[#a3a3a3] uppercase tracking-widest font-medium">Patrimoine net</span>
        <span className="text-sm font-mono font-semibold text-[#3b82f6]">
          {formatCurrency(data[data.length - 1]?.value ?? 0)}
        </span>
      </div>
      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%" minWidth={0} debounce={50}>
          <LineChart data={data} margin={{ top: 4, right: 4, bottom: 0, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f1f1f" vertical={false} />
            <XAxis
              dataKey="date"
              tickFormatter={formatLabel}
              tick={{ fontSize: 11, fill: '#737373' }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip content={<CustomTooltip />} />
            <Line
              type="monotone"
              dataKey="value"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: '#3b82f6', stroke: '#111111', strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
