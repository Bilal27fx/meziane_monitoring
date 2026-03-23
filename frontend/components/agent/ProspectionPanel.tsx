'use client'

import { useState } from 'react'
import { Play, Save, X, Plus } from 'lucide-react'
import { useOpportunites, useMarkOpportuniteVue, useAgentConfig, useSaveAgentConfig } from '@/lib/hooks/useAgent'
import OpportuniteCard from './OpportuniteCard'
import toast from 'react-hot-toast'
import type { Opportunite } from '@/lib/types'

type FilterTab = 'all' | 'nouveau' | 'vu'

export default function ProspectionPanel() {
  const { data: opps = [], isLoading } = useOpportunites()
  const { data: config } = useAgentConfig()
  const markVue = useMarkOpportuniteVue()
  const saveConfig = useSaveAgentConfig()

  const [filterTab, setFilterTab] = useState<FilterTab>('all')
  const [newVille, setNewVille] = useState('')
  const [localConfig, setLocalConfig] = useState({
    villes: config?.villes_cibles ?? ['Paris 18e', 'Lyon 3e', 'Bordeaux'],
    budget: config?.budget_max ?? 400_000,
    tri_min: config?.tri_minimum ?? 5,
    sources: config?.sources ?? ['SeLoger', 'PAP', 'LeBonCoin'],
  })

  const filtered: Opportunite[] =
    filterTab === 'all'
      ? opps
      : opps.filter((o) => o.statut === filterTab)

  const sortedByScore = [...filtered].sort((a, b) => b.score - a.score)

  const addVille = () => {
    const v = newVille.trim()
    if (v && !localConfig.villes.includes(v)) {
      setLocalConfig((c) => ({ ...c, villes: [...c.villes, v] }))
      setNewVille('')
    }
  }

  const removeVille = (ville: string) => {
    setLocalConfig((c) => ({ ...c, villes: c.villes.filter((v) => v !== ville) }))
  }

  const toggleSource = (src: string) => {
    setLocalConfig((c) => ({
      ...c,
      sources: c.sources.includes(src) ? c.sources.filter((s) => s !== src) : [...c.sources, src],
    }))
  }

  const handleSave = async () => {
    try {
      await saveConfig.mutateAsync({
        villes_cibles: localConfig.villes,
        budget_max: localConfig.budget,
        tri_minimum: localConfig.tri_min,
        sources: localConfig.sources,
      })
      toast.success('Configuration sauvegardée')
    } catch {
      toast.error('Erreur lors de la sauvegarde')
    }
  }

  const handleLaunch = async () => {
    toast.success('Agent IA lancé — résultats dans ~2 min')
  }

  const inputClass = 'h-7 text-xs bg-[#0d0d0d] border border-[#262626] rounded px-2 text-white w-full focus:outline-none focus:border-[#404040] font-mono'
  const labelClass = 'text-[9px] text-[#525252] uppercase tracking-wide mb-1 block'

  const FILTER_TABS: { key: FilterTab; label: string }[] = [
    { key: 'all', label: 'Toutes' },
    { key: 'nouveau', label: 'Nouveau' },
    { key: 'vu', label: 'Vu' },
  ]

  return (
    <div className="grid grid-cols-12 gap-3 h-full">
      {/* Config panel */}
      <div className="col-span-4 bg-[#111111] border border-[#262626] rounded-md p-4 overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xs font-semibold text-white">Configuration agent</h3>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#22c55e]" />
            <span className="text-[9px] text-[#737373]">Actif</span>
          </div>
        </div>

        <div className="space-y-4">
          {/* Villes cibles */}
          <div>
            <label className={labelClass}>Villes cibles</label>
            <div className="flex flex-wrap gap-1 mb-1.5">
              {localConfig.villes.map((v) => (
                <span
                  key={v}
                  className="flex items-center gap-1 bg-[#262626] text-[#a3a3a3] text-[9px] rounded px-1.5 py-0.5"
                >
                  {v}
                  <button onClick={() => removeVille(v)} className="hover:text-white">
                    <X className="h-2.5 w-2.5" />
                  </button>
                </span>
              ))}
            </div>
            <div className="flex gap-1">
              <input
                type="text"
                value={newVille}
                onChange={(e) => setNewVille(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && addVille()}
                placeholder="Ajouter une ville..."
                className="flex-1 h-7 text-xs bg-[#0d0d0d] border border-[#262626] rounded px-2 text-white focus:outline-none focus:border-[#404040]"
              />
              <button
                onClick={addVille}
                className="h-7 w-7 flex items-center justify-center bg-[#262626] hover:bg-[#404040] rounded transition-colors"
              >
                <Plus className="h-3 w-3 text-white" />
              </button>
            </div>
          </div>

          {/* Budget max */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className={labelClass}>Budget max</label>
              <span className="text-[9px] font-mono text-[#a3a3a3]">
                {(localConfig.budget / 1000).toFixed(0)}K€
              </span>
            </div>
            <input
              type="range"
              min={50_000}
              max={1_000_000}
              step={10_000}
              value={localConfig.budget}
              onChange={(e) => setLocalConfig((c) => ({ ...c, budget: Number(e.target.value) }))}
              className="w-full accent-[#22c55e]"
            />
          </div>

          {/* TRI minimum */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className={labelClass}>TRI minimum</label>
              <span className="text-[9px] font-mono text-[#a3a3a3]">{localConfig.tri_min}%</span>
            </div>
            <input
              type="range"
              min={1}
              max={20}
              step={0.5}
              value={localConfig.tri_min}
              onChange={(e) => setLocalConfig((c) => ({ ...c, tri_min: Number(e.target.value) }))}
              className="w-full accent-[#22c55e]"
            />
          </div>

          {/* Sources */}
          <div>
            <label className={labelClass}>Sources</label>
            <div className="space-y-1.5">
              {['SeLoger', 'PAP', 'LeBonCoin'].map((src) => (
                <label key={src} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={localConfig.sources.includes(src)}
                    onChange={() => toggleSource(src)}
                    className="accent-[#22c55e]"
                  />
                  <span className="text-xs text-[#a3a3a3]">{src}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Action buttons */}
          <div className="space-y-2 pt-2 border-t border-[#262626]">
            <button
              onClick={handleLaunch}
              className="w-full h-8 flex items-center justify-center gap-1.5 bg-[#22c55e] text-black text-xs font-semibold rounded hover:bg-[#16a34a] transition-colors"
            >
              <Play className="h-3 w-3" />
              Lancer maintenant
            </button>
            <button
              onClick={handleSave}
              disabled={saveConfig.isPending}
              className="w-full h-8 flex items-center justify-center gap-1.5 bg-[#262626] text-white text-xs rounded hover:bg-[#404040] transition-colors disabled:opacity-50"
            >
              <Save className="h-3 w-3" />
              Sauvegarder
            </button>
          </div>
        </div>
      </div>

      {/* Opportunités list */}
      <div className="col-span-8 flex flex-col min-h-0 overflow-hidden">
        {/* Filter tabs */}
        <div className="flex items-center gap-0 border-b border-[#262626] mb-3">
          {FILTER_TABS.map(({ key, label }) => (
            <button
              key={key}
              onClick={() => setFilterTab(key)}
              className={`px-3 py-2 text-xs transition-colors border-b-2 ${
                filterTab === key
                  ? 'text-white border-[#22c55e]'
                  : 'text-[#737373] border-transparent hover:text-white'
              }`}
            >
              {label}
              <span className="ml-1.5 text-[9px] text-[#525252]">
                {key === 'all' ? opps.length : opps.filter((o) => o.statut === key).length}
              </span>
            </button>
          ))}
          <button
            onClick={() => {
              const sorted = [...filtered].sort((a, b) => b.score - a.score)
              // Already sorted by score
            }}
            className="ml-auto px-3 py-2 text-[9px] text-[#525252] hover:text-white transition-colors"
          >
            Score ↓
          </button>
        </div>

        {/* List */}
        <div className="flex-1 overflow-y-auto space-y-2 pr-1">
          {isLoading ? (
            Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-24 bg-[#111111] border border-[#262626] rounded-md animate-pulse" />
            ))
          ) : sortedByScore.length === 0 ? (
            <div className="flex items-center justify-center h-32">
              <p className="text-xs text-[#525252]">Aucune opportunité pour ce filtre</p>
            </div>
          ) : (
            sortedByScore.map((opp) => (
              <OpportuniteCard
                key={opp.id}
                opp={opp}
                onMarkVue={opp.statut === 'nouveau' ? (id) => markVue.mutate(id) : undefined}
              />
            ))
          )}
        </div>
      </div>
    </div>
  )
}
