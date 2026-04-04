'use client'

import { useMemo, useState } from 'react'
import * as Tabs from '@radix-ui/react-tabs'
import AuctionRunsPanel from './AuctionRunsPanel'
import { useAuctionAgentRunEvents, useAuctionAgentRuns } from '@/lib/hooks/useAgent'
import type { AuctionAgentRunEvent } from '@/lib/types'

const TABS = [
  { value: 'encheres', label: 'Enchères' },
  { value: 'legacy', label: 'Legacy' },
]

type DataQualitySummary = {
  normalized_listings: number
  complete_listings: number
  missing_auction_date: number
  missing_visit_dates: number
  missing_visit_location: number
  missing_address: number
  incomplete_samples: Array<{
    listing_id?: number
    source_url?: string
    missing_fields?: string[]
  }>
}

function isDataQualitySummary(value: unknown): value is DataQualitySummary {
  if (!value || typeof value !== 'object') return false
  const candidate = value as Record<string, unknown>
  return (
    typeof candidate.normalized_listings === 'number' &&
    typeof candidate.complete_listings === 'number' &&
    typeof candidate.missing_auction_date === 'number' &&
    typeof candidate.missing_visit_dates === 'number' &&
    typeof candidate.missing_visit_location === 'number' &&
    typeof candidate.missing_address === 'number' &&
    Array.isArray(candidate.incomplete_samples)
  )
}

function extractDataQuality(events: AuctionAgentRunEvent[]): DataQualitySummary | null {
  for (let index = events.length - 1; index >= 0; index -= 1) {
    const payload = events[index]?.payload
    if (!payload || typeof payload !== 'object') continue
    const summary = (payload as Record<string, unknown>).data_quality
    if (isDataQualitySummary(summary)) return summary
  }
  return null
}

function LegacyDataQualityPanel() {
  const { data: runs = [] } = useAuctionAgentRuns()
  const latestRun = runs[0] ?? null
  const { data: events = [], isLoading } = useAuctionAgentRunEvents(latestRun?.id ?? null)

  const quality = useMemo(() => extractDataQuality(events), [events])

  if (!latestRun) {
    return (
      <div className="min-h-[320px] rounded-md border border-[#262626] bg-[#111111] p-6 flex items-center justify-center text-center">
        <div>
          <p className="text-sm text-white">Aucun run Licitor</p>
          <p className="mt-2 text-xs text-[#737373]">Le legacy affichera ici la complétude du dernier run.</p>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return <div className="min-h-[320px] rounded-md border border-[#262626] bg-[#111111] p-6 text-sm text-[#a3a3a3]">Chargement du run #{latestRun.id}…</div>
  }

  if (!quality) {
    return (
      <div className="min-h-[320px] rounded-md border border-[#262626] bg-[#111111] p-6">
        <p className="text-sm text-white">Run #{latestRun.id}</p>
        <p className="mt-2 text-xs text-[#737373]">Aucune synthèse `data_quality` trouvée dans les events de ce run.</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <div className="rounded-md border border-[#262626] bg-[#111111] p-4">
        <p className="text-[10px] uppercase tracking-[0.18em] text-[#6ee7b7]">Legacy</p>
        <h3 className="mt-1 text-sm font-semibold text-white">Complétude du dernier run Licitor</h3>
        <p className="mt-1 text-xs text-[#737373]">Run #{latestRun.id} · statut {latestRun.status}</p>
      </div>

      <div className="grid grid-cols-2 gap-2 md:grid-cols-3">
        {[
          ['Normalisées', quality.normalized_listings],
          ['Complètes', quality.complete_listings],
          ['Sans date enchère', quality.missing_auction_date],
          ['Sans dates visite', quality.missing_visit_dates],
          ['Sans lieu visite', quality.missing_visit_location],
          ['Sans adresse', quality.missing_address],
        ].map(([label, value]) => (
          <div key={label} className="rounded-md border border-[#262626] bg-[#111111] p-3">
            <p className="text-[10px] uppercase tracking-wide text-[#525252]">{label}</p>
            <p className="mt-1 text-lg font-semibold text-white">{String(value)}</p>
          </div>
        ))}
      </div>

      <div className="rounded-md border border-[#262626] bg-[#111111] p-4">
        <p className="text-[10px] uppercase tracking-[0.18em] text-[#737373]">Annonces incomplètes</p>
        {quality.incomplete_samples.length === 0 ? (
          <p className="mt-3 text-sm text-[#d4d4d4]">Aucun échantillon incomplet sur ce run.</p>
        ) : (
          <div className="mt-3 space-y-2">
            {quality.incomplete_samples.map((sample, index) => (
              <div key={`${sample.listing_id ?? 'na'}-${index}`} className="rounded-md border border-[#1f1f1f] bg-[#171717] p-3">
                <p className="text-xs font-semibold text-white">Listing #{sample.listing_id ?? 'N/A'}</p>
                <p className="mt-1 break-all text-[11px] text-[#9ca3af]">{sample.source_url ?? 'URL absente'}</p>
                <p className="mt-2 text-[11px] text-[#fca5a5]">
                  Champs manquants: {sample.missing_fields?.join(', ') || 'non renseignés'}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default function AgentTabs() {
  const [activeTab, setActiveTab] = useState('encheres')

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
        <Tabs.Content value="encheres" className="p-3">
          {activeTab === 'encheres' ? <AuctionRunsPanel /> : null}
        </Tabs.Content>
        <Tabs.Content value="legacy" className="p-3">
          {activeTab === 'legacy' ? <LegacyDataQualityPanel /> : null}
        </Tabs.Content>
      </div>
    </Tabs.Root>
  )
}
