import { Panel } from '@/components/ui/Panel'
import { Bot, Plus, Settings, Zap } from 'lucide-react'

export default function AgentsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-foreground">Agents IA</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Configurez vos agents autonomes pour automatiser vos taches
          </p>
        </div>
        <button className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-foreground hover:bg-accent/90">
          <Plus className="h-4 w-4" />
          Nouvel agent
        </button>
      </div>

      <Panel className="flex flex-col items-center justify-center py-16">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-accent/10 text-accent">
          <Bot className="h-8 w-8" />
        </div>
        <h2 className="mt-4 text-lg font-medium text-foreground">
          Phase 3 - Agents IA
        </h2>
        <p className="mt-2 max-w-md text-center text-sm text-muted-foreground">
          Cette section permettra de configurer des agents autonomes pour automatiser
          les alertes, les relances, et les analyses predictives de votre patrimoine.
        </p>

        <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="flex flex-col items-center rounded-lg bg-secondary/30 p-4">
            <Zap className="h-5 w-5 text-warning" />
            <span className="mt-2 text-xs font-medium text-foreground">
              Alertes automatiques
            </span>
          </div>
          <div className="flex flex-col items-center rounded-lg bg-secondary/30 p-4">
            <Bot className="h-5 w-5 text-accent" />
            <span className="mt-2 text-xs font-medium text-foreground">
              Relances locataires
            </span>
          </div>
          <div className="flex flex-col items-center rounded-lg bg-secondary/30 p-4">
            <Settings className="h-5 w-5 text-positive" />
            <span className="mt-2 text-xs font-medium text-foreground">
              Analyses predictives
            </span>
          </div>
        </div>
      </Panel>
    </div>
  )
}
