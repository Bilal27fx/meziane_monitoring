'use client'

import { useState } from 'react'
import { Panel } from '@/components/ui/Panel'
import { formatCurrency } from '@/lib/utils/format'
import { Calculator, TrendingUp, Wallet, PiggyBank } from 'lucide-react'

export function SimulationPanel() {
  const [prix, setPrix] = useState(300000)
  const [loyer, setLoyer] = useState(1200)
  const [apport, setApport] = useState(60000)

  const rendementBrut = ((loyer * 12) / prix) * 100
  const cashflowMensuel = loyer - (prix - apport) * 0.004 // estimation simplifiee
  const roi = (cashflowMensuel * 12 / apport) * 100

  return (
    <Panel title="Simulation Acquisition" className="h-full">
      <div className="space-y-4">
        {/* Prix */}
        <div>
          <div className="flex items-center justify-between">
            <label className="text-xs text-muted-foreground">Prix achat</label>
            <span className="font-mono text-xs tabular-nums text-foreground">
              {formatCurrency(prix)}
            </span>
          </div>
          <input
            type="range"
            min={100000}
            max={1000000}
            step={10000}
            value={prix}
            onChange={(e) => setPrix(Number(e.target.value))}
            className="mt-2 h-1.5 w-full cursor-pointer appearance-none rounded-full bg-secondary accent-accent"
          />
        </div>

        {/* Loyer */}
        <div>
          <div className="flex items-center justify-between">
            <label className="text-xs text-muted-foreground">Loyer mensuel</label>
            <span className="font-mono text-xs tabular-nums text-foreground">
              {formatCurrency(loyer)}
            </span>
          </div>
          <input
            type="range"
            min={500}
            max={5000}
            step={50}
            value={loyer}
            onChange={(e) => setLoyer(Number(e.target.value))}
            className="mt-2 h-1.5 w-full cursor-pointer appearance-none rounded-full bg-secondary accent-accent"
          />
        </div>

        {/* Apport */}
        <div>
          <div className="flex items-center justify-between">
            <label className="text-xs text-muted-foreground">Apport</label>
            <span className="font-mono text-xs tabular-nums text-foreground">
              {formatCurrency(apport)}
            </span>
          </div>
          <input
            type="range"
            min={10000}
            max={300000}
            step={5000}
            value={apport}
            onChange={(e) => setApport(Number(e.target.value))}
            className="mt-2 h-1.5 w-full cursor-pointer appearance-none rounded-full bg-secondary accent-accent"
          />
        </div>

        {/* Results */}
        <div className="mt-4 grid grid-cols-3 gap-2 rounded-lg bg-secondary/30 p-3">
          <div className="text-center">
            <TrendingUp className="mx-auto h-4 w-4 text-accent" />
            <p className="mt-1 font-mono text-sm font-medium tabular-nums text-foreground">
              {rendementBrut.toFixed(1)}%
            </p>
            <p className="text-[10px] text-muted-foreground">Rdt brut</p>
          </div>
          <div className="text-center">
            <Wallet className="mx-auto h-4 w-4 text-positive" />
            <p className="mt-1 font-mono text-sm font-medium tabular-nums text-positive">
              +{Math.round(cashflowMensuel)} EUR
            </p>
            <p className="text-[10px] text-muted-foreground">CF/mois</p>
          </div>
          <div className="text-center">
            <PiggyBank className="mx-auto h-4 w-4 text-warning" />
            <p className="mt-1 font-mono text-sm font-medium tabular-nums text-foreground">
              {roi.toFixed(1)}%
            </p>
            <p className="text-[10px] text-muted-foreground">ROI</p>
          </div>
        </div>
      </div>
    </Panel>
  )
}
