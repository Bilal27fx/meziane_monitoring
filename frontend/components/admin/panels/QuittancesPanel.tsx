'use client'

import { X, Download, FileText } from 'lucide-react'
import { useQuittances } from '@/lib/hooks/useAdmin'
import Badge from '@/components/ui/Badge'
import { formatCurrency } from '@/lib/utils/format'
import toast from 'react-hot-toast'
import type { Quittance } from '@/lib/types'

interface Props {
  open: boolean
  onClose: () => void
  locataireNom?: string
  locataireId: number | null
}

function statutVariant(statut: Quittance['statut']): 'ok' | 'warning' | 'error' {
  if (statut === 'payee') return 'ok'
  if (statut === 'en_attente') return 'warning'
  return 'error'
}

function statutLabel(statut: Quittance['statut']): string {
  if (statut === 'payee') return 'Payée'
  if (statut === 'en_attente') return 'En attente'
  return 'Impayée'
}

export default function QuittancesPanel({ open, onClose, locataireNom, locataireId }: Props) {
  const { data: quittances = [], isLoading } = useQuittances(locataireId)

  if (!open) return null

  const handleDownload = (mois: string) => {
    toast.success(`Quittance ${mois} téléchargée`)
  }

  const handleGenerate = () => {
    toast.success('Quittance générée et envoyée par email')
  }

  return (
    <>
      {/* Overlay */}
      <div className="fixed inset-0 z-30 bg-black/40" onClick={onClose} />

      {/* Panel */}
      <div className="fixed right-0 top-0 bottom-0 z-40 w-96 bg-[#111111] border-l border-[#262626] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-[#262626]">
          <div>
            <h3 className="text-sm font-semibold text-white">Quittances</h3>
            {locataireNom && (
              <p className="text-xs text-[#737373] mt-0.5">{locataireNom}</p>
            )}
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 flex items-center justify-center rounded text-[#525252] hover:text-white hover:bg-[#262626] transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Table */}
        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="p-4 space-y-2">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="h-10 bg-[#262626]/30 rounded animate-pulse" />
              ))}
            </div>
          ) : (
            <table className="w-full">
              <thead>
                <tr className="border-b border-[#262626]">
                  {['Mois', 'Montant', 'Statut', ''].map((h) => (
                    <th key={h} className="px-3 py-2 text-left text-[9px] text-[#525252] uppercase tracking-wider">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {quittances.map((q) => (
                  <tr
                    key={q.id}
                    className="border-b border-[#262626]/50 hover:bg-[#1a1a1a] transition-colors"
                  >
                    <td className="px-3 py-2.5">
                      <span className="text-xs text-white capitalize">{q.mois}</span>
                    </td>
                    <td className="px-3 py-2.5">
                      <span className="text-xs font-mono text-white tabular-nums">
                        {formatCurrency(q.montant)}
                      </span>
                    </td>
                    <td className="px-3 py-2.5">
                      <Badge variant={statutVariant(q.statut)} dot>
                        {statutLabel(q.statut)}
                      </Badge>
                    </td>
                    <td className="px-3 py-2.5 text-right">
                      <button
                        onClick={() => handleDownload(q.mois)}
                        className="flex items-center gap-1 px-1.5 py-1 text-[9px] text-[#737373] hover:text-white hover:bg-[#262626] rounded transition-colors ml-auto"
                      >
                        <Download className="h-3 w-3" />
                        PDF
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-3 border-t border-[#262626]">
          <button
            onClick={handleGenerate}
            className="w-full h-8 flex items-center justify-center gap-1.5 bg-white text-black text-xs font-medium rounded hover:bg-[#e5e5e5] transition-colors"
          >
            <FileText className="h-3.5 w-3.5" />
            Générer quittance
          </button>
        </div>
      </div>
    </>
  )
}
