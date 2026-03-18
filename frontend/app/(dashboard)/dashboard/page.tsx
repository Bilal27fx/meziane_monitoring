'use client'

import { useEffect, useState } from 'react'
import { KpiCard } from '@/components/dashboard/KpiCard'
import { ChartPanels } from '@/components/dashboard/ChartPanels'
import { TransactionsTable } from '@/components/dashboard/TransactionsTable'
import { TopBiensList } from '@/components/dashboard/TopBiensList'
import { SCIOverviewGrid } from '@/components/dashboard/SCIOverviewGrid'
import { LocatairesList } from '@/components/dashboard/LocatairesList'
import { SimulationPanel } from '@/components/dashboard/SimulationPanel'
import { OpportunitesList } from '@/components/dashboard/OpportunitesList'
import { dashboardApi, type FullDashboardData } from '@/lib/api/dashboard'

export default function DashboardPage() {
  const [data, setData] = useState<FullDashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        setLoading(true)
        setError(null)
        const dashboardData = await dashboardApi.getFullDashboard()
        setData(dashboardData)
      } catch (err) {
        console.error('Error fetching dashboard:', err)
        setError('Impossible de charger les données du dashboard. Vérifiez que le backend est démarré.')
      } finally {
        setLoading(false)
      }
    }

    fetchDashboard()
  }, [])

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="text-center">
          <div className="mb-4 h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent mx-auto"></div>
          <p className="text-sm text-muted-foreground">Chargement du dashboard...</p>
        </div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="text-center max-w-md">
          <div className="mb-4 text-destructive">
            <svg className="h-12 w-12 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="mb-2 text-lg font-semibold">Erreur de connexion</h3>
          <p className="text-sm text-muted-foreground mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground shadow-sm hover:bg-primary/90"
          >
            Réessayer
          </button>
        </div>
      </div>
    )
  }

  // Transform API data to match component props format
  const kpiData = {
    patrimoineNet: {
      label: 'Patrimoine Net',
      value: data.kpi.patrimoine_net,
      change: data.kpi.performance_ytd,
      changeLabel: 'vs année dernière',
      suffix: ' EUR',
      prefix: '',
    },
    cashflowToday: {
      label: 'Cashflow Mensuel',
      value: data.kpi.cashflow_today,
      change: 0, // Calculate from data if available
      changeLabel: 'ce mois',
      suffix: ' EUR',
      prefix: '',
    },
    alertesIA: {
      label: 'Alertes IA',
      value: data.kpi.nb_alertes,
      change: data.kpi.nb_alertes,
      changeLabel: 'alertes actives',
      suffix: '',
      prefix: '',
    },
    performanceYTD: {
      label: 'Taux Occupation',
      value: data.kpi.taux_occupation,
      change: data.kpi.taux_occupation - 90, // Baseline comparison
      changeLabel: 'vs objectif 90%',
      suffix: '%',
      prefix: '',
    },
  }

  return (
    <div className="space-y-6">
      {/* KPI Row - 4 cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard data={kpiData.patrimoineNet} icon="trending" />
        <KpiCard data={kpiData.cashflowToday} icon="activity" />
        <KpiCard data={kpiData.alertesIA} icon="alert" />
        <KpiCard data={kpiData.performanceYTD} icon="trending" />
      </div>

      {/* Charts Row - 2 charts */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        <ChartPanels
          cashflowData={data.cashflow_30j}
          patrimoineData={data.patrimoine_12m}
        />
      </div>

      {/* Data Row 1 - Transactions + Top Biens */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        <TransactionsTable data={data.transactions} />
        <TopBiensList data={data.top_biens} />
      </div>

      {/* Data Row 2 - SCI + Locataires */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        <SCIOverviewGrid data={data.scis} />
        <LocatairesList data={data.locataires} />
      </div>

      {/* Data Row 3 - Simulation + Opportunites */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        <SimulationPanel />
        <OpportunitesList data={data.opportunites} />
      </div>
    </div>
  )
}
