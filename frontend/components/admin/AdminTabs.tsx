'use client'

import * as Tabs from '@radix-ui/react-tabs'
import SCITab from './tabs/SCITab'
import BiensTab from './tabs/BiensTab'
import LocatairesTab from './tabs/LocatairesTab'
import TransactionsTab from './tabs/TransactionsTab'
import SystemTab from './tabs/SystemTab'

const TABS = [
  { value: 'sci', label: 'SCI' },
  { value: 'biens', label: 'Biens' },
  { value: 'locataires', label: 'Locataires' },
  { value: 'transactions', label: 'Transactions' },
  { value: 'systeme', label: 'Système' },
]

export default function AdminTabs() {
  return (
    <Tabs.Root defaultValue="sci" className="flex flex-col h-full">
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

      <div className="flex-1 min-h-0 overflow-auto">
        <Tabs.Content value="sci" className="p-4">
          <SCITab />
        </Tabs.Content>
        <Tabs.Content value="biens" className="p-4">
          <BiensTab />
        </Tabs.Content>
        <Tabs.Content value="locataires" className="p-4">
          <LocatairesTab />
        </Tabs.Content>
        <Tabs.Content value="transactions" className="p-4">
          <TransactionsTab />
        </Tabs.Content>
        <Tabs.Content value="systeme" className="p-4">
          <SystemTab />
        </Tabs.Content>
      </div>
    </Tabs.Root>
  )
}
