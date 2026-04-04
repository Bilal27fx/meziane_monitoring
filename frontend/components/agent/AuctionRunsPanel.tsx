'use client'

import { useMemo, useState } from 'react'
import { ExternalLink, FileSearch, Play, RefreshCcw } from 'lucide-react'
import {
  useAuctionAgentRuns,
  useAuctionListings,
  useLaunchLicitorAuctionRun,
} from '@/lib/hooks/useAgent'
import type { AuctionAgentRun, AuctionListing } from '@/lib/types'
import Modal from '@/components/ui/Modal'
import toast from 'react-hot-toast'

const ELIGIBLE_CATEGORIES = new Set(['prioritaire', 'opportunite_rare'])

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

function listingStatusClasses(status: AuctionListing['status']) {
  switch (status) {
    case 'normalized':
      return 'text-[#60a5fa] border-[#60a5fa]/30 bg-[#60a5fa]/10'
    case 'shortlisted':
      return 'text-[#22c55e] border-[#22c55e]/30 bg-[#22c55e]/10'
    case 'rejected':
      return 'text-[#ef4444] border-[#ef4444]/30 bg-[#ef4444]/10'
    default:
      return 'text-[#a3a3a3] border-[#404040] bg-[#171717]'
  }
}

function formatDateTime(value?: string | null) {
  if (!value) return '—'
  return new Date(value).toLocaleString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatCurrency(value?: number | null) {
  if (typeof value !== 'number') return '—'
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits: 0,
  }).format(value)
}

function detailRows(listing: AuctionListing) {
  return [
    ['Adresse', listing.address ?? '—'],
    ['Ville', listing.city ?? '—'],
    ['Code postal', listing.postal_code ?? '—'],
    ['Type', listing.listing_type ?? '—'],
    ['Surface', listing.surface_m2 ? `${listing.surface_m2} m²` : '—'],
    ['Pièces', listing.nb_pieces ?? '—'],
    ['Chambres', listing.nb_chambres ?? '—'],
    ['Étage', listing.type_etage ?? listing.etage ?? '—'],
    ['Occupation', listing.occupancy_status ?? '—'],
    ['Mise à prix', formatCurrency(listing.reserve_price)],
    ['Loyer estimé', formatCurrency(listing.loyer_estime)],
    ['Rentabilité brute', listing.rentabilite_brute != null ? `${listing.rentabilite_brute.toFixed(1)}%` : '—'],
    ['Score global', listing.score_global ?? '—'],
    ['Catégorie', listing.categorie_investissement ?? '—'],
    ['Prix max cible', formatCurrency(listing.prix_max_cible)],
    ['Prix max agressif', formatCurrency(listing.prix_max_agressif)],
    ['Travaux estimés', formatCurrency(listing.travaux_estimes)],
    ['Valeur marché estimée', formatCurrency(listing.valeur_marche_estimee)],
    ['Valeur marché ajustée', formatCurrency(listing.valeur_marche_ajustee)],
    ['Recommandation', listing.recommandation ?? '—'],
  ]
}

function primaryVisitDate(listing: AuctionListing) {
  return listing.visit_dates?.[0] ?? null
}

function displayValue(value?: string | null, empty = '—') {
  return value ?? empty
}

export default function AuctionRunsPanel() {
  const { data: runs = [], refetch, isFetching } = useAuctionAgentRuns()
  const launchRun = useLaunchLicitorAuctionRun()
  const { data: listings = [], isLoading: isListingsLoading } = useAuctionListings('licitor')
  const [detailListing, setDetailListing] = useState<AuctionListing | null>(null)

  const latestRun = runs[0] ?? null
  const filteredListings = useMemo(
    () =>
      listings.filter(
        (listing) =>
          listing.categorie_investissement != null &&
          ELIGIBLE_CATEGORIES.has(listing.categorie_investissement)
      ),
    [listings]
  )
  const shortlistCount = useMemo(
    () => filteredListings.filter((listing) => listing.status === 'shortlisted').length,
    [filteredListings]
  )

  const handleLaunch = async () => {
    try {
      const result = await launchRun.mutateAsync({ auto_dispatch: true })
      toast.success(`Run #${result.run_id} lancé`)
      refetch()
    } catch {
      toast.error('Erreur lors du lancement du run Licitor')
    }
  }

  return (
    <div className="space-y-2 pb-3">
      <div className="rounded-xl border border-[#262626] bg-[#111111] overflow-hidden">
        <div className="flex flex-col gap-2 px-3 py-3 md:flex-row md:items-center md:justify-between">
          <div className="min-w-0">
            <p className="text-[10px] uppercase tracking-[0.18em] text-[#6ee7b7]">Licitor</p>
            <h3 className="mt-1 text-sm font-semibold text-white">Annonces triées par score</h3>
            <p className="mt-0.5 text-[11px] text-[#737373]">
              Vue compacte des biens avec enchères, visite et accès détail.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => refetch()}
              className="h-9 w-9 rounded-lg border border-[#2a2a2a] bg-[#171717] hover:bg-[#1f1f1f] transition-colors flex items-center justify-center"
              aria-label="Rafraîchir"
            >
              <RefreshCcw className={`h-3.5 w-3.5 text-[#a3a3a3] ${isFetching ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={handleLaunch}
              disabled={launchRun.isPending}
              className="h-9 rounded-lg bg-[#22c55e] px-3 text-xs font-semibold text-black hover:bg-[#16a34a] transition-colors disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center gap-2"
            >
              <Play className="h-3.5 w-3.5" />
              {launchRun.isPending ? 'Lancement...' : 'Lancer Licitor IDF'}
            </button>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-px border-t border-[#262626] bg-[#262626] md:grid-cols-4">
          <div className="bg-[#111111] px-3 py-2.5">
            <p className="text-[10px] uppercase tracking-wide text-[#525252]">Annonces visibles</p>
            <p className="mt-1 text-base font-semibold text-white">{filteredListings.length}</p>
          </div>
          <div className="bg-[#111111] px-3 py-2.5">
            <p className="text-[10px] uppercase tracking-wide text-[#525252]">Shortlist</p>
            <p className="mt-1 text-base font-semibold text-white">{shortlistCount}</p>
          </div>
          <div className="bg-[#111111] px-3 py-2.5">
            <p className="text-[10px] uppercase tracking-wide text-[#525252]">Dernier run</p>
            <p className="mt-1 text-xs font-mono text-white">{latestRun ? `#${latestRun.id}` : '—'}</p>
          </div>
          <div className="bg-[#111111] px-3 py-2.5">
            <p className="text-[10px] uppercase tracking-wide text-[#525252]">Statut</p>
            {latestRun ? (
              <span className={`mt-1 inline-flex px-2 py-1 rounded-full text-[10px] border ${statusClasses(latestRun.status)}`}>
                {latestRun.status}
              </span>
            ) : (
              <p className="mt-1 text-xs text-white">—</p>
            )}
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-[#262626] bg-[#111111] overflow-hidden">
        <div className="flex items-center justify-between gap-4 border-b border-[#262626] px-3 py-2.5">
          <div>
            <h3 className="text-xs font-semibold text-white">Catalogue</h3>
            <p className="mt-1 text-[10px] uppercase tracking-wide text-[#525252]">Lecture rapide</p>
          </div>
          <div className="text-[11px] font-mono text-[#737373]">
            {filteredListings.length} résultat{filteredListings.length > 1 ? 's' : ''}
          </div>
        </div>

        <div className="p-2">
          {isListingsLoading ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 2xl:grid-cols-3 gap-2">
              {Array.from({ length: 4 }).map((_, index) => (
                <div key={index} className="h-36 rounded-xl border border-[#262626] bg-[#171717] animate-pulse" />
              ))}
            </div>
          ) : filteredListings.length === 0 ? (
            <div className="rounded-xl border border-dashed border-[#262626] bg-[#141414] px-6 py-12 text-center">
              <FileSearch className="mx-auto h-6 w-6 text-[#404040]" />
              <p className="mt-4 text-sm text-[#d4d4d4]">Aucune annonce prioritaire ou opportunité rare.</p>
              <p className="mt-2 text-xs text-[#737373]">Lance un run pour recalculer le catalogue Licitor.</p>
            </div>
          ) : (
            <div className="space-y-1.5">
              <div className="hidden rounded-lg border border-[#262626] bg-[#141414] px-3 py-2 text-[10px] uppercase tracking-[0.14em] text-[#6b7280] lg:grid lg:grid-cols-[minmax(0,2.2fr)_minmax(0,1.4fr)_minmax(0,1.3fr)_auto] lg:items-center lg:gap-3">
                <span>Bien</span>
                <span>Enchères</span>
                <span>Visite</span>
                <span>Actions</span>
              </div>
              {filteredListings.map((listing) => (
                <article
                  key={listing.id}
                  className="rounded-lg border border-[#262626] bg-[linear-gradient(180deg,#171717_0%,#121212_100%)] px-3 py-2.5 shadow-[0_8px_20px_rgba(0,0,0,0.14)]"
                >
                  <div className="flex flex-col gap-2 lg:grid lg:grid-cols-[minmax(0,2.2fr)_minmax(0,1.4fr)_minmax(0,1.3fr)_auto] lg:items-start lg:gap-3">
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-1.5">
                        {listing.score_global != null ? (
                          <span className="inline-flex h-6 min-w-[40px] items-center justify-center rounded-md border border-[#1f3a2b] bg-[#0d1711] px-2 text-[10px] font-semibold text-[#bbf7d0]">
                            {listing.score_global}
                          </span>
                        ) : null}
                        <span className={`px-2 py-1 rounded-full text-[9px] font-semibold border ${listingStatusClasses(listing.status)}`}>
                          {listing.status}
                        </span>
                        {listing.categorie_investissement ? (
                          <span className="px-2 py-1 rounded-full text-[9px] font-semibold border border-[#22c55e]/20 bg-[#22c55e]/10 text-[#86efac]">
                            {listing.categorie_investissement}
                          </span>
                        ) : null}
                      </div>

                      <h4 className="mt-1 min-w-0 text-[13px] font-semibold leading-5 text-white">
                        <span className="line-clamp-2">{listing.title}</span>
                      </h4>

                      <p className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1 text-[11px] text-[#9ca3af]">
                        <span>{listing.city ?? 'Ville inconnue'}</span>
                        {listing.surface_m2 ? <span>{listing.surface_m2} m²</span> : null}
                        {listing.nb_pieces ? <span>{listing.nb_pieces} p</span> : null}
                        <span className="font-medium text-[#e5e7eb]">{formatCurrency(listing.reserve_price)}</span>
                      </p>

                      <div className="mt-2 flex flex-wrap items-center gap-1.5">
                        {[
                          listing.loyer_estime ? `Loyer ${formatCurrency(listing.loyer_estime)}` : null,
                          listing.rentabilite_brute != null ? `Renta ${listing.rentabilite_brute.toFixed(1)}%` : null,
                          listing.prix_max_cible || listing.valeur_marche_estimee
                            ? `Prix max ${formatCurrency(listing.prix_max_cible)} · Marché ${formatCurrency(listing.valeur_marche_estimee)}`
                            : null,
                          listing.occupancy_status ? `Occupation ${listing.occupancy_status}` : null,
                        ]
                          .filter(Boolean)
                          .map((item) => (
                            <span
                              key={item}
                              className="inline-flex rounded-md border border-[#2a2a2a] bg-[#111111] px-2 py-1 text-[10px] text-[#d1d5db]"
                            >
                              {item}
                            </span>
                          ))}
                      </div>

                      {listing.raison_score ? (
                        <p className="mt-2 line-clamp-1 text-[10px] text-[#8f8f8f]">{listing.raison_score}</p>
                      ) : null}
                    </div>

                    <div className="rounded-md border border-[#1f3a2b] bg-[#0d1711] px-2.5 py-2">
                      <p className="text-[9px] uppercase tracking-[0.14em] text-[#6ee7b7]">Enchères</p>
                      <p className="mt-1 text-[11px] font-semibold text-white">
                        {listing.auction_date ? formatDateTime(listing.auction_date) : 'Date non renseignée'}
                      </p>
                      <p className="mt-1 line-clamp-2 text-[10px] leading-4 text-[#c7d2cc]">
                        {displayValue(listing.auction_location, 'Lieu non renseigné')}
                      </p>
                      <p className="mt-1 line-clamp-2 text-[10px] leading-4 text-[#8fb3a0]">
                        {displayValue(listing.auction_tribunal, 'Tribunal non renseigné')}
                      </p>
                    </div>

                    <div className="rounded-md border border-[#1e3a5f] bg-[#0d1520] px-2.5 py-2">
                      <p className="text-[9px] uppercase tracking-[0.14em] text-[#93c5fd]">Visite</p>
                      <p className="mt-1 text-[11px] font-semibold text-white">
                        {primaryVisitDate(listing) ?? 'Date non renseignée'}
                      </p>
                      <p className="mt-1 line-clamp-2 text-[10px] leading-4 text-[#cbd5e1]">
                        {displayValue(listing.visit_location, 'Lieu non renseigné')}
                      </p>
                    </div>

                    <div className="flex items-center gap-2 lg:justify-end">
                      <button
                        type="button"
                        onClick={() => setDetailListing(listing)}
                        className="h-8 rounded-md border border-[#303030] bg-[#171717] px-3 text-[10px] font-semibold text-white hover:bg-[#1f1f1f] transition-colors"
                      >
                        Détail
                      </button>
                      <a
                        href={listing.source_url}
                        target="_blank"
                        rel="noreferrer"
                        className="h-8 rounded-md border border-[#24553a] bg-[#12311f] px-3 text-[10px] font-semibold text-[#d1fae5] hover:bg-[#17462c] transition-colors inline-flex items-center gap-1.5"
                      >
                        <ExternalLink className="h-3 w-3" />
                        Lien
                      </a>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>
      </div>

      <Modal
        open={detailListing != null}
        onClose={() => setDetailListing(null)}
        title={detailListing ? `Annonce #${detailListing.id}` : 'Annonce'}
        size="lg"
        position="lower"
      >
        {detailListing ? (
          <div className="space-y-4">
            <div>
              <p className="text-sm font-semibold text-white">{detailListing.title}</p>
              <p className="mt-1 text-xs text-[#737373]">
                {[detailListing.city, detailListing.surface_m2 ? `${detailListing.surface_m2}m²` : null, formatCurrency(detailListing.reserve_price)]
                  .filter(Boolean)
                  .join(' · ')}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="rounded-md border border-[#22c55e]/25 bg-[#0f1a12] p-4">
                <p className="text-[10px] uppercase tracking-[0.18em] text-[#6ee7b7]">Enchères</p>
                <p className="mt-2 text-sm font-semibold text-white">
                  {displayValue(detailListing.auction_tribunal, 'Tribunal non renseigné')}
                </p>
                <p className="mt-2 text-xs text-[#d4d4d4]">
                  Date: {detailListing.auction_date ? formatDateTime(detailListing.auction_date) : '—'}
                </p>
                <p className="mt-1 text-xs text-[#a3a3a3]">
                  Lieu: {displayValue(detailListing.auction_location)}
                </p>
              </div>

              <div className="rounded-md border border-[#3b82f6]/25 bg-[#101722] p-4">
                <p className="text-[10px] uppercase tracking-[0.18em] text-[#93c5fd]">Visite du bien</p>
                <p className="mt-2 text-sm font-semibold text-white">
                  {primaryVisitDate(detailListing) ?? 'Date non renseignée'}
                </p>
                <p className="mt-2 text-xs text-[#d4d4d4]">
                  Lieu: {displayValue(detailListing.visit_location)}
                </p>
                {detailListing.visit_dates && detailListing.visit_dates.length > 1 ? (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {detailListing.visit_dates.slice(1).map((visitDate) => (
                      <span
                        key={visitDate}
                        className="px-2 py-1 rounded border border-[#3b82f6]/20 bg-[#0b1220] text-[11px] text-[#dbeafe]"
                      >
                        {visitDate}
                      </span>
                    ))}
                  </div>
                ) : null}
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-2">
              {detailRows(detailListing).map(([label, value]) => (
                <div key={label} className="border-b border-[#1f1f1f] pb-2">
                  <p className="text-[10px] uppercase tracking-wide text-[#525252]">{label}</p>
                  <p className="mt-1 text-xs text-white break-words">{String(value)}</p>
                </div>
              ))}
            </div>

            {detailListing.raison_score ? (
              <div className="rounded-md border border-[#262626] bg-[#171717] p-3">
                <p className="text-[10px] uppercase tracking-wide text-[#525252]">Analyse</p>
                <p className="mt-2 text-xs text-[#d4d4d4] whitespace-pre-wrap">{detailListing.raison_score}</p>
              </div>
            ) : null}

            {detailListing.risques_llm?.length ? (
              <div className="rounded-md border border-[#262626] bg-[#171717] p-3">
                <p className="text-[10px] uppercase tracking-wide text-[#525252]">Risques</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {detailListing.risques_llm.map((risk) => (
                    <span
                      key={risk}
                      className="px-2 py-1 rounded border border-[#404040] bg-[#111111] text-[11px] text-[#d4d4d4]"
                    >
                      {risk}
                    </span>
                  ))}
                </div>
              </div>
            ) : null}

            {detailListing.property_details ? (
              <div className="rounded-md border border-[#262626] bg-[#171717] p-3">
                <p className="text-[10px] uppercase tracking-wide text-[#525252]">Métadonnées brutes</p>
                <pre className="mt-2 overflow-x-auto whitespace-pre-wrap text-[11px] text-[#d4d4d4]">
                  {JSON.stringify(detailListing.property_details, null, 2)}
                </pre>
              </div>
            ) : null}

            <div className="flex justify-end">
              <a
                href={detailListing.source_url}
                target="_blank"
                rel="noreferrer"
                className="h-9 px-3 rounded-md bg-[#22c55e] text-black text-xs font-semibold hover:bg-[#16a34a] transition-colors inline-flex items-center gap-2"
              >
                <ExternalLink className="h-3.5 w-3.5" />
                Ouvrir l’annonce
              </a>
            </div>
          </div>
        ) : null}
      </Modal>
    </div>
  )
}
