'use client'

import { X, Download, Check } from 'lucide-react'
import { useQuittances, useMarkQuittancePaid } from '@/lib/hooks/useAdmin'
import api from '@/lib/api/client'
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

function extractFilenameFromDisposition(value?: string) {
  if (!value) return null
  const utf8Match = value.match(/filename\*=UTF-8''([^;]+)/i)
  if (utf8Match?.[1]) {
    try {
      return decodeURIComponent(utf8Match[1])
    } catch {
      return utf8Match[1]
    }
  }
  const simpleMatch = value.match(/filename="([^"]+)"/i) || value.match(/filename=([^;]+)/i)
  return simpleMatch?.[1]?.trim() ?? null
}

function sanitizeFilenamePart(value?: string | null) {
  const cleaned = (value ?? 'Locataire')
    .replace(/[\\/:*?"<>|]+/g, ' ')
    .replace(/\s+/g, '-')
    .trim()
    .replace(/^-+|-+$/g, '')
  return cleaned || 'Locataire'
}

function buildFallbackFilename(locataireNom: string | undefined, mois: string) {
  return `${sanitizeFilenamePart(locataireNom)}-${sanitizeFilenamePart(mois)}.pdf`
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
  const markQuittancePaid = useMarkQuittancePaid()

  if (!open) return null

  const handleDownload = async (quittanceId: number, mois: string) => {
    try {
      const response = await api.get(`/api/quittances/${quittanceId}/pdf`, { responseType: 'blob' })
      const blob = response.data instanceof Blob
        ? response.data
        : new Blob([response.data], { type: response.headers['content-type'] ?? 'application/pdf' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = extractFilenameFromDisposition(response.headers['content-disposition']) ?? buildFallbackFilename(locataireNom, mois)
      a.style.display = 'none'
      document.body.appendChild(a)
      a.click()
      window.setTimeout(() => {
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
      }, 1000)
      toast.success(`Quittance ${mois} téléchargée`)
    } catch {
      toast.error('Aucun PDF disponible pour cette quittance')
    }
  }

  const handleMarkPaid = async (quittanceId: number) => {
    try {
      await markQuittancePaid.mutateAsync(quittanceId)
      toast.success('Quittance marquée comme payée')
    } catch {
      toast.error('Erreur lors de la mise à jour')
    }
  }

  return (
    <>
      {/* Overlay */}
      <div className="fixed inset-0 z-30 bg-black/40" onClick={onClose} />

      {/* Panel */}
      <div className="fixed right-0 top-0 bottom-0 z-40 w-[28rem] bg-[#111111] border-l border-[#262626] flex flex-col">
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
                  {['Mois', 'Montant', 'Statut', 'Actions'].map((h) => (
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
                    <td className="px-3 py-2.5">
                      <div className="flex items-center justify-end gap-1 flex-wrap">
                        {q.statut !== 'payee' && (
                          <button
                            onClick={() => handleMarkPaid(q.id)}
                            disabled={markQuittancePaid.isPending}
                            className="inline-flex items-center gap-1 px-2 py-1 text-[10px] font-medium text-[#22c55e] border border-[#22c55e]/30 bg-[#22c55e]/10 hover:text-white hover:bg-[#14532d] rounded transition-colors disabled:opacity-50 whitespace-nowrap"
                          >
                            <Check className="h-3 w-3" />
                            Marquer payée
                          </button>
                        )}
                        <button
                          onClick={() => handleDownload(q.id, q.mois)}
                          className="inline-flex items-center gap-1 px-2 py-1 text-[10px] text-[#737373] hover:text-white hover:bg-[#262626] rounded transition-colors whitespace-nowrap"
                        >
                          <Download className="h-3 w-3" />
                          PDF
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </>
  )
}
