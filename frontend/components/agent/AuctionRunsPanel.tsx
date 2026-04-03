'use client'

import { useEffect, useState } from 'react'
import { Activity, Clock3, FileSearch, Play, RefreshCcw } from 'lucide-react'
import {
  useAuctionAgentRunEvents,
  useAuctionAgentRuns,
  useAuctionListings,
  useLaunchLicitorAuctionRun,
} from '@/lib/hooks/useAgent'
import type { AuctionAgentRun, AuctionAgentRunEvent, AuctionListing } from '@/lib/types'
import toast from 'react-hot-toast'

function statusClasses(status: AuctionAgentRun['status']) {
  switch (status) {
    case 'running':
      return 'text-[#3b82f6] border-[#3b82f6]/30 bg-[#3b82f6]/10'
    case 'success':
      return 'text-[#22c55e] border-[#22c55e]/30 bg-[#22c55e]/10'
    case 'failed':
      return 'text-[#ef4444] border-[#ef4444]/30 bg-[#ef4444]/10'
    case 'cancelled':
      return 'text-[#eab308] border-[#eab308]/30 bg-[#eab308]/10'
    default:
      return 'text-[#a3a3a3] border-[#404040] bg-[#171717]'
  }
}

function levelClasses(level: AuctionAgentRunEvent['level']) {
  switch (level) {
    case 'error':
      return 'text-[#ef4444]'
    case 'warning':
      return 'text-[#eab308]'
    case 'debug':
      return 'text-[#737373]'
    default:
      return 'text-[#a3a3a3]'
  }
}

function formatDateTime(value?: string | null) {
  if (!value) return '—'
  return new Date(value).toLocaleString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

function summarizePayload(payload?: Record<string, unknown> | null) {
  if (!payload) return null

  const parts: string[] = []
  const counters = [
    'sessions_created',
    'sessions_updated',
    'listings_created',
    'listings_updated',
    'listings_normalized',
    'session_pages_processed',
  ]

  for (const key of counters) {
    const value = payload[key]
    if (typeof value === 'number') {
      parts.push(`${key}=${value}`)
    }
  }

  if (typeof payload.url === 'string') {
    parts.unshift(payload.url)
  }

  return parts.length > 0 ? parts.join(' • ') : JSON.stringify(payload)
}

function formatCurrency(value?: number | null) {
  if (typeof value !== 'number') return '—'
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits: 0,
  }).format(value)
}

function filterListingsForRun(listings: AuctionListing[], run: AuctionAgentRun | null) {
  if (!run) return []

  const sourceCode = String(run.parameter_snapshot?.source_code ?? '')
  const startedAt = new Date(run.started_at).getTime()
  const finishedAt = run.finished_at ? new Date(run.finished_at).getTime() : Date.now()

  return listings.filter((listing) => {
    const listingTimestamp = new Date(listing.last_seen_at).getTime()
    const isWithinRunWindow = listingTimestamp >= startedAt - 60_000 && listingTimestamp <= finishedAt + 60_000
    const isMatchingSource = sourceCode === '' || sourceCode === 'licitor'
    return isWithinRunWindow && isMatchingSource
  })
}

export default function AuctionRunsPanel() {
  const { data: runs = [], isLoading, refetch, isFetching } = useAuctionAgentRuns()
  const launchRun = useLaunchLicitorAuctionRun()
  const [selectedRunId, setSelectedRunId] = useState<number | null>(null)
  const [audienceUrlsText, setAudienceUrlsText] = useState('')

  useEffect(() => {
    if (!runs.length) {
      setSelectedRunId(null)
      return
    }

    setSelectedRunId((current) => {
      if (current && runs.some((run) => run.id === current)) {
        return current
      }
      return runs[0].id
    })
  }, [runs])

  const selectedRun = runs.find((run) => run.id === selectedRunId) ?? null
  const { data: events = [], isLoading: isEventsLoading } = useAuctionAgentRunEvents(selectedRunId)
  const sourceCode = selectedRun ? String(selectedRun.parameter_snapshot?.source_code ?? '') : null
  const { data: recentListings = [], isLoading: isListingsLoading } = useAuctionListings(sourceCode)
  const listingsForRun = filterListingsForRun(recentListings, selectedRun)

  const handleLaunch = async () => {
    const audienceUrls = audienceUrlsText
      .split('\n')
      .map((value) => value.trim())
      .filter(Boolean)

    if (audienceUrls.length === 0) {
      toast.error('Ajoute au moins une URL d\'audience Licitor')
      return
    }

    try {
      const result = await launchRun.mutateAsync({ audience_urls: audienceUrls, auto_dispatch: true })
      setAudienceUrlsText('')
      setSelectedRunId(result.run_id)
      toast.success(`Run #${result.run_id} lancé`)
      refetch()
    } catch {
      toast.error('Erreur lors du lancement du run Licitor')
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-3 h-full">
      <div className="lg:col-span-4 min-h-0 rounded-md border border-[#262626] bg-[#111111] overflow-hidden flex flex-col">
        <div className="flex items-center justify-between px-4 py-3 border-b border-[#262626]">
          <div>
            <h3 className="text-xs font-semibold text-white">Runs enchères</h3>
            <p className="text-[10px] text-[#525252] uppercase tracking-wide mt-1">
              Historique et statut des runs
            </p>
          </div>
          <button
            onClick={() => refetch()}
            className="h-8 w-8 rounded border border-[#262626] bg-[#171717] hover:bg-[#1f1f1f] transition-colors flex items-center justify-center"
            aria-label="Rafraîchir les runs"
          >
            <RefreshCcw className={`h-3.5 w-3.5 text-[#a3a3a3] ${isFetching ? 'animate-spin' : ''}`} />
          </button>
        </div>

        <div className="p-3 border-b border-[#262626] space-y-2">
          <label className="block text-[10px] text-[#525252] uppercase tracking-wide">
            URLs audiences Licitor
          </label>
          <textarea
            value={audienceUrlsText}
            onChange={(event) => setAudienceUrlsText(event.target.value)}
            placeholder="https://www.licitor.com/ventes-judiciaires-immobilieres/tj-paris/jeudi-19-mars-2026.html"
            className="w-full min-h-[104px] rounded-md border border-[#262626] bg-[#0d0d0d] px-3 py-2 text-xs text-white font-mono resize-y focus:outline-none focus:border-[#404040]"
          />
          <button
            onClick={handleLaunch}
            disabled={launchRun.isPending}
            className="w-full h-9 rounded-md bg-[#22c55e] text-black text-xs font-semibold hover:bg-[#16a34a] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <Play className="h-3.5 w-3.5" />
            {launchRun.isPending ? 'Lancement...' : 'Creer et dispatcher'}
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-2">
          {isLoading ? (
            Array.from({ length: 4 }).map((_, index) => (
              <div key={index} className="h-24 rounded border border-[#262626] bg-[#171717] animate-pulse" />
            ))
          ) : runs.length === 0 ? (
            <div className="h-full flex items-center justify-center text-center px-6">
              <div>
                <FileSearch className="h-5 w-5 text-[#404040] mx-auto mb-2" />
                <p className="text-xs text-[#737373]">Aucun run auctions pour le moment</p>
              </div>
            </div>
          ) : (
            runs.map((run) => {
              const isSelected = run.id === selectedRunId
              return (
                <button
                  key={run.id}
                  onClick={() => setSelectedRunId(run.id)}
                  className={`w-full text-left rounded-md border p-3 transition-colors ${
                    isSelected
                      ? 'border-[#22c55e]/40 bg-[#0f1a12]'
                      : 'border-[#262626] bg-[#171717] hover:bg-[#1b1b1b]'
                  }`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <span className="text-xs font-mono text-white">run #{run.id}</span>
                    <span className={`px-2 py-1 rounded text-[10px] border ${statusClasses(run.status)}`}>
                      {run.status}
                    </span>
                  </div>
                  <div className="mt-2 space-y-1 text-[11px] text-[#737373]">
                    <p>Agent #{run.agent_definition_id}</p>
                    <p>{formatDateTime(run.started_at)}</p>
                    <p className="truncate">
                      source: {String(run.parameter_snapshot?.source_code ?? 'n/a')}
                    </p>
                  </div>
                </button>
              )
            })
          )}
        </div>
      </div>

      <div className="lg:col-span-8 min-h-0 rounded-md border border-[#262626] bg-[#111111] overflow-hidden flex flex-col">
        <div className="px-4 py-3 border-b border-[#262626]">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h3 className="text-xs font-semibold text-white">Timeline d&apos;exécution</h3>
              <p className="text-[10px] text-[#525252] uppercase tracking-wide mt-1">
                Événements persistés du run sélectionné
              </p>
            </div>
            {selectedRun ? (
              <div className="flex items-center gap-2 text-[11px] text-[#737373]">
                <Clock3 className="h-3.5 w-3.5" />
                {formatDateTime(selectedRun.finished_at ?? selectedRun.started_at)}
              </div>
            ) : null}
          </div>
        </div>

        {!selectedRun ? (
          <div className="flex-1 flex items-center justify-center text-center px-6">
            <div>
              <Activity className="h-5 w-5 text-[#404040] mx-auto mb-2" />
              <p className="text-xs text-[#737373]">Sélectionne un run pour voir ce que l&apos;agent a fait</p>
            </div>
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            <div className="rounded-md border border-[#262626] bg-[#171717] p-3 grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3">
              <div>
                <p className="text-[10px] text-[#525252] uppercase tracking-wide">Run</p>
                <p className="mt-1 text-sm font-mono text-white">#{selectedRun.id}</p>
              </div>
              <div>
                <p className="text-[10px] text-[#525252] uppercase tracking-wide">Statut</p>
                <p className="mt-1 text-sm text-white">{selectedRun.status}</p>
              </div>
              <div>
                <p className="text-[10px] text-[#525252] uppercase tracking-wide">Début</p>
                <p className="mt-1 text-sm text-white">{formatDateTime(selectedRun.started_at)}</p>
              </div>
              <div>
                <p className="text-[10px] text-[#525252] uppercase tracking-wide">Fin</p>
                <p className="mt-1 text-sm text-white">{formatDateTime(selectedRun.finished_at)}</p>
              </div>
            </div>

            <div className="rounded-md border border-[#262626] bg-[#171717]">
              <div className="px-3 py-2 border-b border-[#262626] flex items-center justify-between gap-3">
                <div>
                  <p className="text-xs font-semibold text-white">Résultats ingérés</p>
                  <p className="text-[10px] text-[#525252] uppercase tracking-wide mt-1">
                    Annonces visibles pour le run sélectionné
                  </p>
                </div>
                <span className="text-[10px] font-mono text-[#737373]">
                  {listingsForRun.length} résultat{listingsForRun.length > 1 ? 's' : ''}
                </span>
              </div>
              <div className="p-3 space-y-2">
                {isListingsLoading ? (
                  Array.from({ length: 2 }).map((_, index) => (
                    <div key={index} className="h-20 rounded border border-[#262626] bg-[#111111] animate-pulse" />
                  ))
                ) : listingsForRun.length === 0 ? (
                  <div className="rounded-md border border-dashed border-[#262626] p-4 text-center">
                    <p className="text-xs text-[#737373]">Aucune annonce visible pour ce run pour l&apos;instant</p>
                  </div>
                ) : (
                  listingsForRun.map((listing) => (
                    <a
                      key={listing.id}
                      href={listing.source_url}
                      target="_blank"
                      rel="noreferrer"
                      className="block rounded-md border border-[#262626] bg-[#111111] p-3 hover:bg-[#151515] transition-colors"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="text-sm text-white">{listing.title}</p>
                          <p className="mt-1 text-[11px] text-[#737373]">
                            {listing.city ?? 'Ville inconnue'}
                            {listing.postal_code ? ` • ${listing.postal_code}` : ''}
                            {listing.surface_m2 ? ` • ${listing.surface_m2} m²` : ''}
                          </p>
                        </div>
                        <span className={`px-2 py-1 rounded text-[10px] border ${statusClasses(listing.status)}`}>
                          {listing.status}
                        </span>
                      </div>
                      <div className="mt-2 flex flex-wrap gap-3 text-[11px] text-[#a3a3a3]">
                        <span>Mise à prix: {formatCurrency(listing.reserve_price)}</span>
                        <span>Occupation: {listing.occupancy_status ?? 'n/a'}</span>
                        <span>Vu le {formatDateTime(listing.last_seen_at)}</span>
                      </div>
                    </a>
                  ))
                )}
              </div>
            </div>

            {isEventsLoading ? (
              Array.from({ length: 5 }).map((_, index) => (
                <div key={index} className="h-16 rounded border border-[#262626] bg-[#171717] animate-pulse" />
              ))
            ) : events.length === 0 ? (
              <div className="rounded-md border border-dashed border-[#262626] p-6 text-center">
                <p className="text-xs text-[#737373]">Aucun événement persisté sur ce run</p>
              </div>
            ) : (
              events.map((event) => (
                <div key={event.id} className="rounded-md border border-[#262626] bg-[#171717] p-3">
                  <div className="flex items-center gap-3">
                    <span className="text-[10px] font-mono text-[#525252]">
                      {formatDateTime(event.created_at)}
                    </span>
                    <span className={`text-[10px] uppercase tracking-wide ${levelClasses(event.level)}`}>
                      {event.level}
                    </span>
                    <span className="text-[10px] text-[#737373]">{event.step ?? 'run'}</span>
                    <span className="ml-auto text-[10px] font-mono text-[#525252]">{event.event_type}</span>
                  </div>
                  <p className="mt-2 text-sm text-white">{event.message}</p>
                  {summarizePayload(event.payload) ? (
                    <p className="mt-2 text-[11px] text-[#737373] break-all">
                      {summarizePayload(event.payload)}
                    </p>
                  ) : null}
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  )
}
