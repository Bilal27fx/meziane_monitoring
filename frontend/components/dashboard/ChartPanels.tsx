'use client'

import dynamic from 'next/dynamic'
import type { CashflowPoint, PatrimoinePoint } from '@/lib/types/dashboard'
import { Panel } from '@/components/ui/Panel'

// Import dynamique pour éviter les warnings SSR de Recharts
const CashflowChart = dynamic(
  () => import('./CashflowChart').then((mod) => mod.CashflowChart),
  {
    ssr: false,
    loading: () => (
      <Panel title="Cashflow 30 jours" className="h-full">
        <div className="flex h-72 items-center justify-center">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-accent border-t-transparent" />
        </div>
      </Panel>
    ),
  }
)

const PatrimoineChart = dynamic(
  () => import('./PatrimoineChart').then((mod) => mod.PatrimoineChart),
  {
    ssr: false,
    loading: () => (
      <Panel title="Evolution Patrimoine 12 mois" className="h-full">
        <div className="flex h-72 items-center justify-center">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-accent border-t-transparent" />
        </div>
      </Panel>
    ),
  }
)

interface ChartPanelsProps {
  cashflowData: CashflowPoint[]
  patrimoineData: PatrimoinePoint[]
}

export function ChartPanels({ cashflowData, patrimoineData }: ChartPanelsProps) {
  return (
    <>
      <CashflowChart data={cashflowData} />
      <PatrimoineChart data={patrimoineData} />
    </>
  )
}
