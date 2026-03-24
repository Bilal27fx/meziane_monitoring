'use client'

import { Building2, TrendingUp, Users, DollarSign } from 'lucide-react'
import KPICard from '@/components/dashboard/KPICard'
import CashflowChart from '@/components/dashboard/CashflowChart'
import PatrimoineChart from '@/components/dashboard/PatrimoineChart'
import SCIOverview from '@/components/dashboard/SCIOverview'
import Top5Biens from '@/components/dashboard/Top5Biens'
import TransactionsTable from '@/components/dashboard/TransactionsTable'
import SimulationForm from '@/components/dashboard/SimulationForm'
import OpportunitesWidget from '@/components/dashboard/OpportunitesWidget'
import LocatairesCards from '@/components/dashboard/LocatairesCards'
import { useFullDashboard } from '@/lib/hooks/useDashboard'
import { formatCurrency } from '@/lib/utils/format'

function formatKPI(value: number): string {
  if (!value && value !== 0) return '—'
  if (Math.abs(value) >= 1_000_000) return `${(value / 1_000_000).toFixed(2)}M€`
  if (Math.abs(value) >= 1_000) return `${Math.round(value / 1_000)}K€`
  return `${value}€`
}

export default function DashboardPage() {
  const { data, isLoading } = useFullDashboard()
  const kpi = data?.kpi

  const nbBiens = data?.sci_overview.reduce((sum, s) => sum + s.nb_biens, 0) ?? 0

  const cashflowChartData = data?.cashflow_30days?.map(d => ({ date: d.date, value: d.net }))
  const patrimoineChartData = data?.patrimoine_12months?.map(d => ({ date: d.date, value: d.valeur }))

  return (
    <div className="min-h-[calc(100vh-56px)] p-4 overflow-y-auto">
      <div
        className="grid grid-cols-12 gap-3"
        style={{ gridTemplateRows: 'auto auto auto auto' }}
      >
        {/* Row 1 — KPI cards */}
        <div className="col-span-3">
          <KPICard
            title="Patrimoine net"
            value={isLoading ? '…' : formatKPI(kpi?.patrimoine_net ?? 0)}
            icon={Building2}
          />
        </div>
        <div className="col-span-3">
          <KPICard
            title="Cashflow ce mois"
            value={isLoading ? '…' : formatCurrency(kpi?.cashflow_today ?? 0)}
            icon={DollarSign}
          />
        </div>
        <div className="col-span-3">
          <KPICard
            title="Taux d'occupation"
            value={isLoading ? '…' : `${kpi?.taux_occupation?.toFixed(1) ?? '—'}%`}
            icon={TrendingUp}
          />
        </div>
        <div className="col-span-3">
          <KPICard
            title="Biens en portefeuille"
            value={isLoading ? '…' : String(nbBiens || '—')}
            icon={Users}
            subtitle={data ? `${data.sci_overview.length} SCI · ${kpi?.nb_locataires_actifs ?? 0} locataires` : undefined}
          />
        </div>

        {/* Row 2 — Charts + SCI + Top5 */}
        <div className="col-span-3">
          <CashflowChart data={cashflowChartData} />
        </div>
        <div className="col-span-3">
          <PatrimoineChart data={patrimoineChartData} />
        </div>
        <div className="col-span-3">
          <SCIOverview data={data?.sci_overview} />
        </div>
        <div className="col-span-3 row-span-2">
          <Top5Biens data={data?.top_biens} />
        </div>

        {/* Row 3 — Transactions */}
        <div className="col-span-9">
          <TransactionsTable data={data?.recent_transactions} />
        </div>

        {/* Row 4 — Simulation + Opportunites + Locataires */}
        <div className="col-span-3">
          <SimulationForm />
        </div>
        <div className="col-span-4">
          <OpportunitesWidget />
        </div>
        <div className="col-span-5">
          <LocatairesCards />
        </div>
      </div>
    </div>
  )
}
