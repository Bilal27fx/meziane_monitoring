import { Panel } from '@/components/ui/Panel'
import Link from 'next/link'
import { Building2, Users, BarChart3, PieChart, ChevronRight } from 'lucide-react'

const adminSections = [
  {
    title: 'Biens',
    description: 'Gerez vos biens immobiliers',
    href: '/admin/biens',
    icon: Building2,
    count: 5,
  },
  {
    title: 'SCI',
    description: 'Gerez vos societes civiles immobilieres',
    href: '/admin/sci',
    icon: PieChart,
    count: 2,
  },
  {
    title: 'Locataires',
    description: 'Gerez vos locataires et baux',
    href: '/admin/locataires',
    icon: Users,
    count: 5,
  },
  {
    title: 'Analytics',
    description: 'Rapports et statistiques avancees',
    href: '/admin/analytics',
    icon: BarChart3,
    count: null,
  },
]

export default function AdminPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-foreground">Administration</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Gerez votre patrimoine immobilier
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {adminSections.map((section) => {
          const Icon = section.icon

          return (
            <Link key={section.href} href={section.href}>
              <Panel className="group h-full cursor-pointer transition-colors hover:border-accent/50">
                <div className="flex items-start justify-between">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent/10 text-accent">
                    <Icon className="h-5 w-5" />
                  </div>
                  {section.count !== null && (
                    <span className="font-mono text-2xl font-semibold tabular-nums text-foreground">
                      {section.count}
                    </span>
                  )}
                </div>

                <div className="mt-4">
                  <div className="flex items-center gap-2">
                    <h2 className="text-base font-medium text-foreground">
                      {section.title}
                    </h2>
                    <ChevronRight className="h-4 w-4 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100" />
                  </div>
                  <p className="mt-1 text-sm text-muted-foreground">
                    {section.description}
                  </p>
                </div>

                <div className="mt-4 text-xs text-muted-foreground">
                  Phase 3 - CRUD complet
                </div>
              </Panel>
            </Link>
          )
        })}
      </div>
    </div>
  )
}
