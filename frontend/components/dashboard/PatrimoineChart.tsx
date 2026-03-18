'use client'

import { Panel } from '@/components/ui/Panel'
import type { PatrimoinePoint } from '@/lib/types/dashboard'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { formatCurrency } from '@/lib/utils/format'

interface PatrimoineChartProps {
  data: PatrimoinePoint[]
}

export function PatrimoineChart({ data }: PatrimoineChartProps) {
  return (
    <Panel title="Evolution Patrimoine 12 mois" className="h-full">
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorPatrimoine" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--chart-2)" stopOpacity={0.3} />
                <stop offset="95%" stopColor="var(--chart-2)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="var(--border)"
              vertical={false}
            />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 10, fill: 'var(--muted-foreground)' }}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              tick={{ fontSize: 10, fill: 'var(--muted-foreground)' }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(value) => `${(value / 1000000).toFixed(1)}M`}
              width={45}
              domain={['dataMin - 100000', 'dataMax + 100000']}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'var(--card)',
                border: '1px solid var(--border)',
                borderRadius: '8px',
                fontSize: '12px',
              }}
              labelStyle={{ color: 'var(--foreground)' }}
              formatter={(value: number) => [formatCurrency(value), 'Valeur']}
            />
            <Line
              type="monotone"
              dataKey="valeur"
              stroke="var(--chart-2)"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: 'var(--chart-2)' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Panel>
  )
}
