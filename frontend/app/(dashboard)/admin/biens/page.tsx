import { Panel } from '@/components/ui/Panel'
import { Building2, Plus } from 'lucide-react'

export default function BiensPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-foreground">Biens</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Gerez votre portefeuille immobilier
          </p>
        </div>
        <button className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-foreground hover:bg-accent/90">
          <Plus className="h-4 w-4" />
          Ajouter un bien
        </button>
      </div>

      <Panel className="flex flex-col items-center justify-center py-16">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-accent/10 text-accent">
          <Building2 className="h-8 w-8" />
        </div>
        <h2 className="mt-4 text-lg font-medium text-foreground">
          Phase 3 - Gestion des Biens
        </h2>
        <p className="mt-2 max-w-md text-center text-sm text-muted-foreground">
          Cette section permettra d&apos;ajouter, modifier et supprimer vos biens immobiliers
          avec toutes leurs caracteristiques.
        </p>
      </Panel>
    </div>
  )
}
