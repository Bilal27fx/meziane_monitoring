'use client'

import { useState } from 'react'
import { Eye, ArrowRight, X } from 'lucide-react'
import Modal from '@/components/ui/Modal'
import Badge from '@/components/ui/Badge'
import { formatCurrency, formatPercentRaw } from '@/lib/utils/format'
import type { Opportunite } from '@/lib/types'

function scoreVariant(score: number): 'ok' | 'warning' | 'error' {
  if (score >= 85) return 'ok'
  if (score >= 70) return 'warning'
  return 'error'
}

function scoreStyle(score: number) {
  if (score >= 85) return { bg: 'bg-[#22c55e]/20', text: 'text-[#22c55e]', border: 'border-[#22c55e]/40' }
  if (score >= 70) return { bg: 'bg-[#eab308]/20', text: 'text-[#eab308]', border: 'border-[#eab308]/40' }
  return { bg: 'bg-[#ef4444]/20', text: 'text-[#ef4444]', border: 'border-[#ef4444]/40' }
}

function dpeColor(dpe?: string): string {
  const map: Record<string, string> = { A: '#22c55e', B: '#84cc16', C: '#eab308', D: '#f97316', E: '#ef4444', F: '#dc2626', G: '#991b1b' }
  return map[dpe ?? ''] ?? '#737373'
}

interface Props {
  opp: Opportunite
  onMarkVue?: (id: number) => void
}

export default function OpportuniteCard({ opp, onMarkVue }: Props) {
  const [modalOpen, setModalOpen] = useState(false)
  const s = scoreStyle(opp.score)

  return (
    <>
      <div className="bg-[#111111] border border-[#262626] rounded-md p-3 hover:border-[#404040] transition-colors">
        <div className="flex items-start gap-3">
          {/* Score circle */}
          <div
            className={`w-10 h-10 rounded-full flex-shrink-0 flex items-center justify-center border ${s.bg} ${s.border}`}
          >
            <span className={`text-xs font-mono font-bold ${s.text}`}>{opp.score}</span>
          </div>

          {/* Main info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <div>
                <p className="text-sm text-white font-medium truncate">{opp.adresse}</p>
                <p className="text-xs text-[#737373]">{opp.ville}</p>
              </div>
              <Badge variant={opp.statut === 'nouveau' ? 'info' : 'default'}>
                {opp.statut === 'nouveau' ? 'NOUVEAU' : 'VU'}
              </Badge>
            </div>

            <div className="flex items-center gap-3 mt-2">
              <span className="font-mono text-sm text-white tabular-nums">
                {formatCurrency(opp.prix)}
              </span>
              {opp.surface && (
                <span className="text-xs text-[#525252]">{opp.surface}m²</span>
              )}
              {opp.nb_pieces && (
                <span className="text-xs text-[#525252]">{opp.nb_pieces}P</span>
              )}
              {opp.tri_estime !== undefined && (
                <span className="text-xs font-mono text-[#22c55e]">
                  TRI {formatPercentRaw(opp.tri_estime)}
                </span>
              )}
              {opp.dpe && (
                <span
                  className="text-[9px] font-bold px-1.5 py-0.5 rounded"
                  style={{ color: dpeColor(opp.dpe), background: `${dpeColor(opp.dpe)}22` }}
                >
                  DPE {opp.dpe}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 mt-3 pt-2 border-t border-[#262626]">
          {opp.statut === 'nouveau' && onMarkVue && (
            <button
              onClick={() => onMarkVue(opp.id)}
              className="flex items-center gap-1 px-2 py-1 text-xs text-[#737373] bg-[#1a1a1a] hover:bg-[#262626] rounded transition-colors"
            >
              <Eye className="h-3 w-3" />
              Marquer VU
            </button>
          )}
          <button
            onClick={() => setModalOpen(true)}
            className="flex items-center gap-1 px-2 py-1 text-xs text-white bg-[#262626] hover:bg-[#404040] rounded transition-colors ml-auto"
          >
            Analyser
            <ArrowRight className="h-3 w-3" />
          </button>
        </div>
      </div>

      {/* Analysis Modal */}
      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={`Analyse — ${opp.adresse}`} size="lg">
        <div className="space-y-4">
          {/* Header metrics */}
          <div className="grid grid-cols-4 gap-2">
            {[
              { label: 'Prix', value: formatCurrency(opp.prix) },
              { label: 'TRI estimé', value: opp.tri_estime ? formatPercentRaw(opp.tri_estime) : '—' },
              { label: 'Score IA', value: `${opp.score}/100` },
              { label: 'DPE', value: opp.dpe ?? '—' },
            ].map(({ label, value }) => (
              <div key={label} className="bg-[#0d0d0d] border border-[#262626] rounded p-2">
                <p className="text-[9px] text-[#525252] uppercase">{label}</p>
                <p className="text-sm font-mono text-white mt-0.5">{value}</p>
              </div>
            ))}
          </div>

          {/* AI Analysis */}
          {opp.analyse_ia && (
            <div>
              <p className="text-[10px] text-[#737373] uppercase tracking-wide mb-1.5">Analyse IA</p>
              <div className="bg-[#0d0d0d] border border-[#262626] rounded p-3">
                <p className="text-xs text-[#a3a3a3] leading-relaxed">{opp.analyse_ia}</p>
              </div>
            </div>
          )}

          {/* Risks */}
          {opp.risques && opp.risques.length > 0 && (
            <div>
              <p className="text-[10px] text-[#737373] uppercase tracking-wide mb-1.5">Points de vigilance</p>
              <div className="space-y-1.5">
                {opp.risques.map((risk, i) => (
                  <div key={i} className="flex items-start gap-2 bg-[#eab308]/5 border border-[#eab308]/20 rounded p-2">
                    <span className="text-[#eab308] mt-0.5 flex-shrink-0">⚠</span>
                    <p className="text-xs text-[#a3a3a3]">{risk}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Quick simulation */}
          <div>
            <p className="text-[10px] text-[#737373] uppercase tracking-wide mb-1.5">Simulation rapide (20% apport)</p>
            <div className="grid grid-cols-3 gap-2">
              {(() => {
                const apport = opp.prix * 0.2
                const loyer = opp.prix * 0.0055
                const mensualite = opp.prix * 0.8 * (3.5 / 100 / 12) * Math.pow(1 + 3.5 / 100 / 12, 240) / (Math.pow(1 + 3.5 / 100 / 12, 240) - 1)
                const cashflow = loyer - mensualite - 200
                return [
                  { label: 'Apport estimé', value: formatCurrency(apport) },
                  { label: 'Mensualité', value: formatCurrency(mensualite) + '/m' },
                  { label: 'Cashflow net', value: (cashflow >= 0 ? '+' : '') + formatCurrency(cashflow) + '/m', positive: cashflow >= 0 },
                ].map(({ label, value, positive }) => (
                  <div key={label} className="bg-[#0d0d0d] border border-[#262626] rounded p-2">
                    <p className="text-[9px] text-[#525252] uppercase">{label}</p>
                    <p className={`text-xs font-mono mt-0.5 ${positive === undefined ? 'text-white' : positive ? 'text-[#22c55e]' : 'text-[#ef4444]'}`}>{value}</p>
                  </div>
                ))
              })()}
            </div>
          </div>

          {opp.url && (
            <a
              href={opp.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-xs text-[#3b82f6] hover:text-[#60a5fa] transition-colors"
            >
              Voir l'annonce originale →
            </a>
          )}
        </div>
      </Modal>
    </>
  )
}
