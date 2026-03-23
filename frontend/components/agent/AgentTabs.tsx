'use client'

import * as Tabs from '@radix-ui/react-tabs'
import ProspectionPanel from './ProspectionPanel'
import TasksTable from './TasksTable'
import LogsViewer from './LogsViewer'

const TABS = [
  { value: 'prospection', label: 'Prospection' },
  { value: 'taches', label: 'Tâches' },
  { value: 'logs', label: 'Logs' },
]

export default function AgentTabs() {
  return (
    <Tabs.Root defaultValue="prospection" className="flex flex-col h-full">
      {/* Tab triggers */}
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

      {/* Tab content */}
      <div className="flex-1 min-h-0 overflow-hidden">
        <Tabs.Content value="prospection" className="h-full p-3 overflow-hidden">
          <ProspectionPanel />
        </Tabs.Content>
        <Tabs.Content value="taches" className="h-full p-3 overflow-y-auto">
          <TasksTable />
        </Tabs.Content>
        <Tabs.Content value="logs" className="h-full p-3 overflow-hidden">
          <LogsViewer />
        </Tabs.Content>
      </div>
    </Tabs.Root>
  )
}
