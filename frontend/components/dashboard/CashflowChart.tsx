'use client'

import { Panel } from '@/components/ui/Panel'
import type { CashflowPoint } from '@/lib/types/dashboard'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'
import { formatCurrency } from '@/lib/utils/format'

interface CashflowChartProps {
  data: CashflowPoint[]
}

export function CashflowChart({ data }: CashflowChartProps) {
  return (
    <Panel title="Cashflow 30 jours" className="h-full">
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorNet" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--chart-1)" stopOpacity={0.3} />
                <stop offset="95%" stopColor="var(--chart-1)" stopOpacity={0} />
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
              tickFormatter={(value) => {
                const date = new Date(value)
                return `${date.getDate()}/${date.getMonth() + 1}`
              }}
            />
            <YAxis
              tick={{ fontSize: 10, fill: 'var(--muted-foreground)' }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`}
              width={40}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'var(--card)',
                border: '1px solid var(--border)',
                borderRadius: '8px',
                fontSize: '12px',
              }}
              labelStyle={{ color: 'var(--foreground)' }}
              formatter={(value: number, name: string) => [
                formatCurrency(value),
                name === 'net' ? 'Net' : name === 'entrees' ? 'Entrées' : 'Sorties',
              ]}
              labelFormatter={(label) => {
                const date = new Date(label)
                return date.toLocaleDateString('fr-FR')
              }}
            />
            <ReferenceLine y={0} stroke="var(--border)" />
            <Area
              type="monotone"
              dataKey="net"
              stroke="var(--chart-1)"
              strokeWidth={2}
              fill="url(#colorNet)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </Panel>
  )
}
