'use client'

import { useState } from 'react'
import * as Tabs from '@radix-ui/react-tabs'
import AuctionRunsPanel from './AuctionRunsPanel'

const TABS = [
  { value: 'encheres', label: 'Enchères' },
  { value: 'legacy', label: 'Legacy' },
]

export default function AgentTabs() {
  const [activeTab, setActiveTab] = useState('encheres')

  return (
    <Tabs.Root value={activeTab} onValueChange={setActiveTab} className="flex flex-col h-full">
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

      <div className="flex-1 min-h-0 overflow-hidden">
        <Tabs.Content value="encheres" className="h-full p-3 overflow-hidden">
          {activeTab === 'encheres' ? <AuctionRunsPanel /> : null}
        </Tabs.Content>
        <Tabs.Content value="legacy" className="h-full p-3 overflow-hidden">
          <div className="h-full rounded-md border border-[#262626] bg-[#111111] p-6 flex items-center justify-center text-center">
            <div>
              <p className="text-sm text-white">Panneaux legacy désactivés</p>
              <p className="mt-2 text-xs text-[#737373]">
                Les anciens appels <code>/api/agent/*</code> ne sont pas branchés sur ce backend.
                L’espace agent est recentré sur le domaine enchères pour éviter le bruit 404.
              </p>
            </div>
          </div>
        </Tabs.Content>
      </div>
    </Tabs.Root>
  )
}
