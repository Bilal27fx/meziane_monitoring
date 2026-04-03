'use client'

import { useEffect, useMemo, useState } from 'react'
import { X, Wallet } from 'lucide-react'
import { ResponsiveContainer, AreaChart, Area, CartesianGrid, Tooltip, XAxis } from 'recharts'
import { useCreateLocatairePayment, useLocatairePayments } from '@/lib/hooks/useAdmin'
import Badge from '@/components/ui/Badge'
import { formatCurrency, formatDate } from '@/lib/utils/format'
import type { Locataire, LocatairePaiementMonthStatus } from '@/lib/types'
import toast from 'react-hot-toast'

interface Props {
  open: boolean
  onClose: () => void
  locataire: Locataire | null
}

function statusVariant(statut: LocatairePaiementMonthStatus['statut']) {
  if (statut === 'payee') return 'ok' as const
  if (statut === 'partielle') return 'info' as const
  if (statut === 'en_attente' || statut === 'a_generer') return 'warning' as const
  return 'error' as const
}

function statusLabel(statut: LocatairePaiementMonthStatus['statut']) {
  if (statut === 'payee') return 'Payée'
  if (statut === 'partielle') return 'Partielle'
  if (statut === 'impayee') return 'Impayée'
  if (statut === 'a_generer') return 'À générer'
  return 'En attente'
}

function modePaiementLabel(mode: string) {
  if (mode === 'virement') return 'Virement'
  if (mode === 'prelevement') return 'Prélèvement'
  if (mode === 'carte') return 'Carte'
  if (mode === 'cheque') return 'Chèque'
  if (mode === 'especes') return 'Espèces'
  return 'Autre'
}

function monthShortLabel(key: string) {
  const [year, month] = key.split('-').map(Number)
  return new Date(year, month - 1, 1).toLocaleDateString('fr-FR', { month: 'short' })
}

function ChartTooltip({ active, payload, label }: { active?: boolean; payload?: Array<{ value: number; color: string; name: string }>; label?: string }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-[#1a1a1a] border border-[#404040] rounded-md px-3 py-2 shadow-lg">
      <p className="text-xs text-[#a3a3a3] mb-2">{label}</p>
      {payload.map((entry) => (
        <p key={entry.name} className="text-xs font-mono" style={{ color: entry.color }}>
          {entry.name}: {formatCurrency(entry.value)}
        </p>
      ))}
    </div>
  )
}

export default function LocatairePaymentsPanel({ open, onClose, locataire }: Props) {
  const { data, isLoading } = useLocatairePayments(locataire?.id ?? null)
  const createPayment = useCreateLocatairePayment()
  const [periodView, setPeriodView] = useState<'mensuel' | 'annuel'>('mensuel')
  const [isMounted, setIsMounted] = useState(false)
  const monthlyHistory = data?.historique_mensuel ?? data?.derniers_mois ?? []
  const yearlySummary = data?.resume_annuel ?? []
  const payments = data?.paiements ?? []

  useEffect(() => {
    setIsMounted(true)
  }, [])

  const monthlyChartData = useMemo(() => {
    const source = [...monthlyHistory].reverse().slice(-12)
    return source.map((item) => ({
      key: item.key,
      label: monthShortLabel(item.key),
      du: item.montant_du,
      paye: item.montant_paye,
      reste: item.solde,
    }))
  }, [monthlyHistory])

  const handleValidateMonth = async (item: LocatairePaiementMonthStatus) => {
    if (!locataire?.id || item.solde <= 0) return
    try {
      await createPayment.mutateAsync({
        locataireId: locataire.id,
        data: {
          montant: item.solde,
          date_paiement: new Date().toISOString().slice(0, 10),
          mode_paiement: 'virement',
          quittance_id: item.quittance_id,
          periode_key: item.key,
          note: `Validation depuis le suivi locataire pour ${item.label}`,
        },
      })
      toast.success(`${item.label} validé`)
    } catch {
      toast.error(`Impossible de valider ${item.label}`)
    }
  }

  if (!open) return null

  return (
    <>
      <div className="fixed inset-0 z-30 bg-black/40" onClick={onClose} />

      <div className="fixed right-0 top-0 bottom-0 z-40 w-[34rem] bg-[#111111] border-l border-[#262626] flex flex-col">
        <div className="flex items-center justify-between px-4 py-3 border-b border-[#262626]">
          <div>
            <h3 className="text-sm font-semibold text-white">Paiements locataire</h3>
            {locataire && <p className="text-xs text-[#737373] mt-0.5">{locataire.prenom} {locataire.nom}</p>}
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 flex items-center justify-center rounded text-[#525252] hover:text-white hover:bg-[#262626] transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="p-4 space-y-3">
              {Array.from({ length: 6 }).map((_, index) => (
                <div key={index} className="h-16 bg-[#262626]/30 rounded animate-pulse" />
              ))}
            </div>
          ) : !data?.bail_id ? (
            <div className="p-6 text-center">
              <div className="w-11 h-11 mx-auto mb-3 rounded-full bg-[#1a1a1a] border border-[#262626] flex items-center justify-center">
                <Wallet className="h-5 w-5 text-[#737373]" />
              </div>
              <p className="text-sm text-white">Aucun bail exploitable</p>
              <p className="text-xs text-[#737373] mt-1">Le suivi paiement sera disponible dès qu’un bail sera rattaché au locataire.</p>
            </div>
          ) : (
            <div className="p-4 space-y-4">
              <div className="bg-[#0d0d0d] border border-[#262626] rounded-lg p-3">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-[10px] uppercase tracking-wide text-[#525252]">Bail</p>
                    <p className="text-xs text-white mt-1">
                      Depuis {data.date_debut_bail ? formatDate(data.date_debut_bail) : '—'}
                      {data.date_fin_bail ? ` jusqu’au ${formatDate(data.date_fin_bail)}` : ''}
                    </p>
                  </div>
                  <Badge variant={data.reste_a_payer > 0 ? 'warning' : 'ok'} dot>
                    {data.reste_a_payer > 0 ? 'Solde en cours' : 'À jour'}
                  </Badge>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                {[
                  { label: 'Mensuel', value: formatCurrency(data.montant_mensuel) },
                  { label: 'Payé cumulé', value: formatCurrency(data.total_paye) },
                  { label: 'Reste à payer', value: formatCurrency(data.reste_a_payer) },
                  { label: 'Échéances réglées', value: `${data.mensualites_reglees}/${data.mensualites_total}` },
                ].map((item) => (
                  <div key={item.label} className="bg-[#0d0d0d] border border-[#262626] rounded-lg p-3">
                    <p className="text-[10px] uppercase tracking-wide text-[#525252]">{item.label}</p>
                    <p className="text-sm text-white font-semibold mt-1">{item.value}</p>
                  </div>
                ))}
              </div>

              <div className="bg-[#0d0d0d] border border-[#262626] rounded-lg overflow-hidden">
                <div className="px-3 py-2 border-b border-[#262626] flex items-center justify-between gap-3">
                  <p className="text-[10px] uppercase tracking-wide text-[#525252]">Visualisation</p>
                  <div className="inline-flex rounded-md border border-[#262626] overflow-hidden">
                    {[
                      { key: 'mensuel', label: 'Mensuel' },
                      { key: 'annuel', label: 'Annuel' },
                    ].map((tab) => (
                      <button
                        key={tab.key}
                        onClick={() => setPeriodView(tab.key as 'mensuel' | 'annuel')}
                        className={`px-2.5 py-1 text-[10px] transition-colors ${
                          periodView === tab.key ? 'bg-[#1f3a2a] text-[#86efac]' : 'bg-transparent text-[#737373] hover:text-white'
                        }`}
                      >
                        {tab.label}
                      </button>
                    ))}
                  </div>
                </div>
                {periodView === 'mensuel' ? (
                  <div className="p-3">
                    <div className="h-48 min-h-[12rem] w-full">
                      {isMounted ? (
                        <ResponsiveContainer width="100%" height="100%" minWidth={260} minHeight={180} debounce={50}>
                          <AreaChart data={monthlyChartData} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
                            <defs>
                              <linearGradient id="dueFill" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.25} />
                                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                              </linearGradient>
                              <linearGradient id="paidFill" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                              </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1f1f1f" vertical={false} />
                            <XAxis
                              dataKey="label"
                              tick={{ fontSize: 11, fill: '#737373' }}
                              axisLine={false}
                              tickLine={false}
                            />
                            <Tooltip content={<ChartTooltip />} />
                            <Area type="monotone" dataKey="du" name="Dû" stroke="#3b82f6" fill="url(#dueFill)" strokeWidth={2} />
                            <Area type="monotone" dataKey="paye" name="Payé" stroke="#22c55e" fill="url(#paidFill)" strokeWidth={2} />
                          </AreaChart>
                        </ResponsiveContainer>
                      ) : (
                        <div className="h-full w-full rounded-md bg-[#111111]" />
                      )}
                    </div>
                    <p className="text-[10px] text-[#737373] mt-2">Lecture des 12 derniers mois: montant dû vs montant payé.</p>
                  </div>
                ) : (
                  <div className="divide-y divide-[#262626]">
                    {yearlySummary.map((year) => (
                      <div key={year.annee} className="px-3 py-3 grid grid-cols-[auto_1fr_auto] gap-3 items-center">
                        <div className="text-sm font-semibold text-white">{year.annee}</div>
                        <div className="text-[10px] text-[#737373]">
                          {year.mensualites_reglees}/{year.mensualites_total} mois réglés • Dû {formatCurrency(year.total_du)} • Payé {formatCurrency(year.total_paye)}
                        </div>
                        <span className={`text-xs font-mono tabular-nums ${year.reste_a_payer > 0 ? 'text-[#eab308]' : 'text-[#22c55e]'}`}>
                          {formatCurrency(year.reste_a_payer)}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="bg-[#0d0d0d] border border-[#262626] rounded-lg overflow-hidden">
                <div className="px-3 py-2 border-b border-[#262626]">
                  <p className="text-[10px] uppercase tracking-wide text-[#525252]">Suivi mensuel</p>
                </div>
                <div className="divide-y divide-[#262626]">
                  {monthlyHistory.map((item) => (
                    <div key={item.key} className="px-3 py-3 grid grid-cols-[1.2fr_auto_auto_auto] gap-3 items-center">
                      <div>
                        <p className="text-xs text-white">{item.label}</p>
                        <p className="text-[10px] text-[#737373] mt-1">
                          Dû {formatCurrency(item.montant_du)} • Payé {formatCurrency(item.montant_paye)}
                          {item.date_paiement ? ` • ${formatDate(item.date_paiement)}` : ''}
                        </p>
                      </div>
                      <Badge variant={statusVariant(item.statut)} dot>
                        {statusLabel(item.statut)}
                      </Badge>
                      <span className={`text-xs font-mono tabular-nums ${item.solde > 0 ? 'text-[#eab308]' : 'text-[#22c55e]'}`}>
                        {formatCurrency(item.solde)}
                      </span>
                      {item.solde > 0 ? (
                        <button
                          onClick={() => handleValidateMonth(item)}
                          disabled={createPayment.isPending}
                          className="inline-flex items-center justify-center px-2 py-1 text-[10px] font-medium text-[#22c55e] border border-[#22c55e]/30 bg-[#22c55e]/10 hover:text-white hover:bg-[#14532d] rounded transition-colors disabled:opacity-50 whitespace-nowrap"
                        >
                          Valider
                        </button>
                      ) : (
                        <span className="text-[10px] text-[#525252] text-right">Réglé</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-[#0d0d0d] border border-[#262626] rounded-lg overflow-hidden">
                <div className="px-3 py-2 border-b border-[#262626]">
                  <p className="text-[10px] uppercase tracking-wide text-[#525252]">Paiements validés</p>
                </div>
                <div className="divide-y divide-[#262626]">
                  {payments.length ? payments.map((paiement) => (
                    <div key={paiement.id} className="px-3 py-3 flex items-center justify-between gap-3">
                      <div>
                        <p className="text-xs text-white">{modePaiementLabel(paiement.mode_paiement)}</p>
                        <p className="text-[10px] text-[#737373] mt-1">
                          {formatDate(paiement.date_paiement)}
                          {paiement.reference ? ` • Réf. ${paiement.reference}` : ''}
                        </p>
                      </div>
                      <span className="text-xs font-mono text-white tabular-nums">{formatCurrency(paiement.montant)}</span>
                    </div>
                  )) : (
                    <div className="px-3 py-6 text-center text-xs text-[#737373]">
                      Aucun paiement enregistré pour ce locataire.
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  )
}
