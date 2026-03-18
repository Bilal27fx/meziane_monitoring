import { Panel } from '@/components/ui/Panel'
import { BarChart3 } from 'lucide-react'

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-foreground">Analytics</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Rapports et statistiques avancees
        </p>
      </div>

      <Panel className="flex flex-col items-center justify-center py-16">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-accent/10 text-accent">
          <BarChart3 className="h-8 w-8" />
        </div>
        <h2 className="mt-4 text-lg font-medium text-foreground">
          Phase 3 - Analytics
        </h2>
        <p className="mt-2 max-w-md text-center text-sm text-muted-foreground">
          Cette section permettra de visualiser des rapports detailles,
          des tendances et des projections sur votre patrimoine.
        </p>
      </Panel>
    </div>
  )
}
