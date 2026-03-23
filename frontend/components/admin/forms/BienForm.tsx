'use client'

import { useState } from 'react'
import { useCreateBien, useUpdateBien, useSCIs } from '@/lib/hooks/useAdmin'
import toast from 'react-hot-toast'
import type { Bien, BienFormData } from '@/lib/types'

interface Props {
  bien?: Bien
  onClose: () => void
}

const inputClass = 'w-full h-8 text-xs bg-[#0d0d0d] border border-[#262626] rounded px-2.5 text-white focus:outline-none focus:border-[#404040] transition-colors'
const labelClass = 'text-[9px] text-[#525252] uppercase tracking-wide block mb-1'
const sectionClass = 'text-[10px] text-[#737373] uppercase tracking-widest mb-2 mt-4 first:mt-0 pb-1 border-b border-[#262626]'

export default function BienForm({ bien, onClose }: Props) {
  const createBien = useCreateBien()
  const updateBien = useUpdateBien()
  const { data: scisData } = useSCIs()
  const scis = scisData?.items ?? []

  const [form, setForm] = useState<BienFormData>({
    sci_id: bien?.sci_id ?? (scis[0]?.id ?? 0),
    adresse: bien?.adresse ?? '',
    complement: bien?.complement ?? '',
    ville: bien?.ville ?? '',
    code_postal: bien?.code_postal ?? '',
    type: bien?.type ?? 'appartement',
    surface: bien?.surface ?? undefined,
    nb_pieces: bien?.nb_pieces ?? undefined,
    etage: bien?.etage ?? undefined,
    dpe: bien?.dpe ?? '',
    validite_dpe: bien?.validite_dpe ?? '',
    prix_acquisition: bien?.prix_acquisition ?? undefined,
    date_acquisition: bien?.date_acquisition ?? '',
    valeur_actuelle: bien?.valeur_actuelle ?? undefined,
    statut: bien?.statut ?? 'loue',
  })

  const set = <K extends keyof BienFormData>(key: K, value: BienFormData[K]) => {
    setForm((f) => ({ ...f, [key]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (bien) {
        await updateBien.mutateAsync({ id: bien.id, data: form })
        toast.success('Bien mis à jour')
      } else {
        await createBien.mutateAsync(form)
        toast.success('Bien créé')
      }
      onClose()
    } catch {
      toast.error('Erreur lors de la sauvegarde')
    }
  }

  const isPending = createBien.isPending || updateBien.isPending

  return (
    <form onSubmit={handleSubmit} className="space-y-2 max-h-[60vh] overflow-y-auto pr-1">
      {/* Section Localisation */}
      <p className={sectionClass}>Localisation</p>
      <div>
        <label className={labelClass}>SCI *</label>
        <select
          value={form.sci_id}
          onChange={(e) => set('sci_id', Number(e.target.value))}
          className={inputClass}
          required
        >
          {scis.map((s) => (
            <option key={s.id} value={s.id}>{s.nom}</option>
          ))}
        </select>
      </div>
      <div>
        <label className={labelClass}>Adresse *</label>
        <input
          type="text"
          value={form.adresse}
          onChange={(e) => set('adresse', e.target.value)}
          className={inputClass}
          required
          placeholder="12 Rue du Commerce"
        />
      </div>
      <div>
        <label className={labelClass}>Complément</label>
        <input
          type="text"
          value={form.complement ?? ''}
          onChange={(e) => set('complement', e.target.value)}
          className={inputClass}
          placeholder="Apt 3, Bât B"
        />
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className={labelClass}>Ville *</label>
          <input
            type="text"
            value={form.ville}
            onChange={(e) => set('ville', e.target.value)}
            className={inputClass}
            required
            placeholder="Paris"
          />
        </div>
        <div>
          <label className={labelClass}>Code postal *</label>
          <input
            type="text"
            value={form.code_postal}
            onChange={(e) => set('code_postal', e.target.value)}
            className={inputClass}
            required
            placeholder="75015"
          />
        </div>
      </div>

      {/* Section Caractéristiques */}
      <p className={sectionClass}>Caractéristiques</p>
      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className={labelClass}>Type *</label>
          <select
            value={form.type}
            onChange={(e) => set('type', e.target.value)}
            className={inputClass}
            required
          >
            {['appartement', 'maison', 'bureau', 'commerce', 'terrain', 'parking'].map((t) => (
              <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>
            ))}
          </select>
        </div>
        <div>
          <label className={labelClass}>Surface (m²)</label>
          <input
            type="number"
            value={form.surface ?? ''}
            onChange={(e) => set('surface', Number(e.target.value) || undefined)}
            className={inputClass}
            placeholder="48"
          />
        </div>
        <div>
          <label className={labelClass}>Nb pièces</label>
          <input
            type="number"
            value={form.nb_pieces ?? ''}
            onChange={(e) => set('nb_pieces', Number(e.target.value) || undefined)}
            className={inputClass}
            placeholder="2"
          />
        </div>
        <div>
          <label className={labelClass}>Étage</label>
          <input
            type="number"
            value={form.etage ?? ''}
            onChange={(e) => set('etage', Number(e.target.value) || undefined)}
            className={inputClass}
            placeholder="3"
          />
        </div>
        <div>
          <label className={labelClass}>DPE</label>
          <select
            value={form.dpe ?? ''}
            onChange={(e) => set('dpe', e.target.value)}
            className={inputClass}
          >
            <option value="">—</option>
            {['A', 'B', 'C', 'D', 'E', 'F', 'G'].map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        </div>
        <div>
          <label className={labelClass}>Validité DPE</label>
          <input
            type="date"
            value={form.validite_dpe ?? ''}
            onChange={(e) => set('validite_dpe', e.target.value)}
            className={inputClass}
          />
        </div>
      </div>

      {/* Section Financier */}
      <p className={sectionClass}>Financier</p>
      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className={labelClass}>Prix acquisition * (€)</label>
          <input
            type="number"
            value={form.prix_acquisition ?? ''}
            onChange={(e) => set('prix_acquisition', Number(e.target.value) || undefined)}
            className={inputClass}
            placeholder="350000"
            required
          />
        </div>
        <div>
          <label className={labelClass}>Date acquisition</label>
          <input
            type="date"
            value={form.date_acquisition ?? ''}
            onChange={(e) => set('date_acquisition', e.target.value)}
            className={inputClass}
          />
        </div>
        <div>
          <label className={labelClass}>Valeur actuelle (€)</label>
          <input
            type="number"
            value={form.valeur_actuelle ?? ''}
            onChange={(e) => set('valeur_actuelle', Number(e.target.value) || undefined)}
            className={inputClass}
            placeholder="380000"
          />
        </div>
        <div>
          <label className={labelClass}>Statut</label>
          <select
            value={form.statut}
            onChange={(e) => set('statut', e.target.value)}
            className={inputClass}
          >
            {['loue', 'vacant', 'travaux', 'vente'].map((s) => (
              <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="flex gap-2 pt-3 sticky bottom-0 bg-[#111111]">
        <button
          type="button"
          onClick={onClose}
          className="flex-1 h-8 text-xs text-[#737373] bg-[#1a1a1a] hover:bg-[#262626] rounded transition-colors"
        >
          Annuler
        </button>
        <button
          type="submit"
          disabled={isPending}
          className="flex-1 h-8 text-xs text-black bg-white hover:bg-[#e5e5e5] rounded font-medium transition-colors disabled:opacity-50"
        >
          {isPending ? 'Sauvegarde…' : bien ? 'Mettre à jour' : 'Créer le bien'}
        </button>
      </div>
    </form>
  )
}
