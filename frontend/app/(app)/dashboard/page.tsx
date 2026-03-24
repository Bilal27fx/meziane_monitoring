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
  const kpis = data?.kpis

  return (
    <div className="h-[calc(100vh-56px)] p-3 overflow-hidden">
      <div
        className="grid grid-cols-12 gap-2"
        style={{ gridTemplateRows: '56px 192px 192px 192px', height: '100%' }}
      >
        {/* Row 1 — KPI cards */}
        <div className="col-span-3">
          <KPICard
            title="Patrimoine net"
            value={isLoading ? '…' : formatKPI(kpis?.patrimoine_net ?? 0)}
            change={kpis?.patrimoine_net_change}
            trend={kpis?.patrimoine_net_change !== undefined ? (kpis.patrimoine_net_change >= 0 ? 'up' : 'down') : undefined}
            icon={Building2}
          />
        </div>
        <div className="col-span-3">
          <KPICard
            title="Cashflow mensuel"
            value={isLoading ? '…' : formatCurrency(kpis?.cashflow_mensuel ?? 0)}
            change={kpis?.cashflow_mensuel_change}
            trend={kpis?.cashflow_mensuel_change !== undefined ? (kpis.cashflow_mensuel_change >= 0 ? 'up' : 'down') : undefined}
            icon={DollarSign}
          />
        </div>
        <div className="col-span-3">
          <KPICard
            title="Taux d'occupation"
            value={isLoading ? '…' : `${kpis?.taux_occupation?.toFixed(1) ?? '—'}%`}
            change={kpis?.taux_occupation_change}
            trend={kpis?.taux_occupation_change !== undefined ? (kpis.taux_occupation_change >= 0 ? 'up' : 'down') : undefined}
            icon={TrendingUp}
          />
        </div>
        <div className="col-span-3">
          <KPICard
            title="Biens en portefeuille"
            value={isLoading ? '…' : String(kpis?.nb_biens ?? '—')}
            icon={Users}
            subtitle={data ? `${data.sci_overview.length} SCI · ${data.locataires_actifs} locataires` : undefined}
          />
        </div>

        {/* Row 2 — Charts + SCI + Top5 (row-span-3) */}
        <div className="col-span-3">
          <CashflowChart data={data?.cashflow_history} />
        </div>
        <div className="col-span-3">
          <PatrimoineChart data={data?.patrimoine_history} />
        </div>
        <div className="col-span-3">
          <SCIOverview data={data?.sci_overview} />
        </div>
        <div className="col-span-3 row-span-3">
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
        <div className="col-span-3">
          <OpportunitesWidget />
        </div>
        <div className="col-span-3">
          <LocatairesCards />
        </div>
      </div>
    </div>
  )
}
