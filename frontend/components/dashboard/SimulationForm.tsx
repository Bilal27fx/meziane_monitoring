'use client'

import { useState, useMemo } from 'react'
import { calcMensualite, calcTriBrut, calcTriNet, calcCashflow } from '@/lib/utils/calc'
import { formatCurrency, formatPercentRaw } from '@/lib/utils/format'
import { cn } from '@/lib/utils/cn'

const CHARGES_DEFAULT = 200

function triTextColor(tri: number): string {
  if (tri >= 7) return 'text-[#22c55e]'
  if (tri >= 4) return 'text-[#eab308]'
  return 'text-[#ef4444]'
}

export default function SimulationForm() {
  const [prix, setPrix] = useState(250_000)
  const [apport, setApport] = useState(50_000)
  const [taux, setTaux] = useState(3.5)

  const results = useMemo(() => {
    const loyer = prix * 0.0055
    const mensualite = calcMensualite(prix, apport, taux)
    const cashflow = calcCashflow(loyer, mensualite, CHARGES_DEFAULT)
    const triBrut = calcTriBrut(loyer, prix)
    const triNet = calcTriNet(cashflow, prix)
    return { loyer, mensualite, cashflow, triBrut, triNet }
  }, [prix, apport, taux])

  const inputClass =
    'h-7 text-xs font-mono bg-[#0d0d0d] border border-[#262626] rounded px-2 text-white w-full focus:outline-none focus:border-[#404040] tabular-nums'
  const labelClass = 'text-[9px] text-[#525252] uppercase tracking-wide mb-0.5 block'

  return (
    <div className="h-48 p-2 bg-[#111111] border border-[#262626] rounded-md flex flex-col">
      <span className="text-[10px] text-[#737373] uppercase tracking-wide mb-2">Simulateur</span>

      <div className="grid grid-cols-3 gap-1.5 mb-2">
        <div>
          <label className={labelClass}>Prix €</label>
          <input
            type="number"
            className={inputClass}
            value={prix}
            onChange={(e) => setPrix(Number(e.target.value))}
            min={0}
          />
        </div>
        <div>
          <label className={labelClass}>Apport €</label>
          <input
            type="number"
            className={inputClass}
            value={apport}
            onChange={(e) => setApport(Number(e.target.value))}
            min={0}
          />
        </div>
        <div>
          <label className={labelClass}>Taux %</label>
          <input
            type="number"
            className={inputClass}
            value={taux}
            onChange={(e) => setTaux(Number(e.target.value))}
            min={0}
            max={20}
            step={0.1}
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-1 flex-1">
        <div className="bg-[#0d0d0d] border border-[#262626] rounded p-1.5">
          <span className="text-[9px] text-[#525252] uppercase block">Mensualité</span>
          <span className="text-xs font-mono text-white tabular-nums">
            {formatCurrency(results.mensualite)}/m
          </span>
        </div>
        <div className="bg-[#0d0d0d] border border-[#262626] rounded p-1.5">
          <span className="text-[9px] text-[#525252] uppercase block">Cashflow net</span>
          <span
            className={cn(
              'text-xs font-mono tabular-nums',
              results.cashflow >= 0 ? 'text-[#22c55e]' : 'text-[#ef4444]'
            )}
          >
            {results.cashflow >= 0 ? '+' : ''}{formatCurrency(results.cashflow)}/m
          </span>
        </div>
        <div className="bg-[#0d0d0d] border border-[#262626] rounded p-1.5">
          <span className="text-[9px] text-[#525252] uppercase block">TRI Brut</span>
          <span className={cn('text-xs font-mono tabular-nums', triTextColor(results.triBrut))}>
            {formatPercentRaw(results.triBrut)}
          </span>
        </div>
        <div className="bg-[#0d0d0d] border border-[#262626] rounded p-1.5">
          <span className="text-[9px] text-[#525252] uppercase block">TRI Net</span>
          <span className={cn('text-xs font-mono tabular-nums', triTextColor(results.triNet))}>
            {formatPercentRaw(results.triNet)}
          </span>
        </div>
      </div>
    </div>
  )
}
