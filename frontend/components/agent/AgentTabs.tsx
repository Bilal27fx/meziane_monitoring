'use client'

import { useState } from 'react'
import * as Tabs from '@radix-ui/react-tabs'

const TABS = [
  { value: 'overview', label: 'Overview' },
  { value: 'roadmap', label: 'Roadmap' },
]

export default function AgentTabs() {
  const [activeTab, setActiveTab] = useState('overview')

  return (
    <Tabs.Root value={activeTab} onValueChange={setActiveTab} className="flex flex-col min-h-full">
      <Tabs.List className="flex items-center gap-0 border-b border-[#262626] flex-shrink-0">
        {TABS.map(({ value, label }) => (
          <Tabs.Trigger
            key={value}
            value={value}
            className="px-4 py-3 text-xs text-[#737373] border-b-2 border-transparent transition-colors data-[state=active]:text-white data-[state=active]:border-[#22c55e] hover:text-white"
          >
            {label}
          </Tabs.Trigger>
        ))}
      </Tabs.List>

      <div className="flex-1 min-h-0">
        <Tabs.Content value="overview" className="p-3">
          <div className="space-y-3">
            <section className="rounded-xl border border-[#262626] bg-[#111111] p-5">
              <p className="text-[10px] uppercase tracking-[0.18em] text-[#6ee7b7]">Reconstruction</p>
              <h2 className="mt-2 text-lg font-semibold text-white">Module agent remis à zéro</h2>
              <p className="mt-2 max-w-2xl text-sm text-[#a3a3a3]">
                Toute la logique backend historique a été retirée. Cette page conserve uniquement le squelette UI
                pour préparer la prochaine version du module.
              </p>
            </section>

            <section className="grid gap-3 md:grid-cols-3">
              {[
                ['Statut', 'Backend supprimé'],
                ['Données live', 'Désactivées'],
                ['Prochaine étape', 'Redéfinir le nouveau périmètre'],
              ].map(([label, value]) => (
                <div key={label} className="rounded-xl border border-[#262626] bg-[#111111] p-4">
                  <p className="text-[10px] uppercase tracking-wide text-[#525252]">{label}</p>
                  <p className="mt-2 text-sm font-semibold text-white">{value}</p>
                </div>
              ))}
            </section>

            <section className="rounded-xl border border-dashed border-[#2f2f2f] bg-[#141414] p-5">
              <p className="text-xs font-semibold text-white">Zone vide volontaire</p>
              <p className="mt-2 text-sm text-[#8a8a8a]">
                Utiliser cette surface pour redessiner le futur agent: orchestration, exécution, suivi, ou autre
                workflow dédié.
              </p>
            </section>
          </div>
        </Tabs.Content>
        <Tabs.Content value="roadmap" className="p-3">
          <div className="rounded-xl border border-[#262626] bg-[#111111] p-5">
            <p className="text-[10px] uppercase tracking-[0.18em] text-[#737373]">Roadmap</p>
            <div className="mt-4 space-y-3">
              {[
                'Définir le but exact du nouveau module agent.',
                'Fixer les entrées/sorties API minimales avant toute implémentation backend.',
                'Construire un premier flux vertical simple, testé, sans héritage de l’ancien système.',
              ].map((item) => (
                <div key={item} className="rounded-lg border border-[#1f1f1f] bg-[#171717] px-4 py-3 text-sm text-[#d4d4d4]">
                  {item}
                </div>
              ))}
            </div>
          </div>
        </Tabs.Content>
      </div>
    </Tabs.Root>
  )
}
