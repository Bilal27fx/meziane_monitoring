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

export default function DashboardPage() {
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
            value="2.39M€"
            change={3.2}
            trend="up"
            icon={Building2}
          />
        </div>
        <div className="col-span-3">
          <KPICard
            title="Cashflow mensuel"
            value="4 215€"
            change={1.8}
            trend="up"
            icon={DollarSign}
          />
        </div>
        <div className="col-span-3">
          <KPICard
            title="Taux d'occupation"
            value="91.7%"
            change={-0.5}
            trend="down"
            icon={TrendingUp}
          />
        </div>
        <div className="col-span-3">
          <KPICard
            title="Biens en portefeuille"
            value="7"
            icon={Users}
            subtitle="3 SCI · 7 locataires"
          />
        </div>

        {/* Row 2 — Charts + SCI + Top5 (row-span-3) */}
        <div className="col-span-3">
          <CashflowChart />
        </div>
        <div className="col-span-3">
          <PatrimoineChart />
        </div>
        <div className="col-span-3">
          <SCIOverview />
        </div>
        <div className="col-span-3 row-span-3">
          <Top5Biens />
        </div>

        {/* Row 3 — Transactions */}
        <div className="col-span-9">
          <TransactionsTable />
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
