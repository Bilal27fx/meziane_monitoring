'use client'

import { useState } from 'react'
import { useCreateSCI, useUpdateSCI } from '@/lib/hooks/useAdmin'
import toast from 'react-hot-toast'
import type { SCI, SCIFormData } from '@/lib/types'

interface Props {
  sci?: SCI
  onClose: () => void
}

const inputClass = 'w-full h-8 text-xs bg-[#0d0d0d] border border-[#262626] rounded px-2.5 text-white focus:outline-none focus:border-[#404040] transition-colors'
const labelClass = 'text-[9px] text-[#525252] uppercase tracking-wide block mb-1'

export default function SCIForm({ sci, onClose }: Props) {
  const createSCI = useCreateSCI()
  const updateSCI = useUpdateSCI()

  const [form, setForm] = useState<SCIFormData>({
    nom: sci?.nom ?? '',
    siret: sci?.siret ?? '',
    forme_juridique: sci?.forme_juridique ?? 'SCI',
    capital: sci?.capital ?? undefined,
    siege_social: sci?.siege_social ?? '',
    gerant_nom: sci?.gerant_nom ?? '',
    gerant_prenom: sci?.gerant_prenom ?? '',
    date_creation: sci?.date_creation ?? '',
  })

  const [errors, setErrors] = useState<{ nom?: string; siret?: string }>({})

  const set = (key: keyof SCIFormData, value: string | number) => {
    setForm((f) => ({ ...f, [key]: value }))
    if (key === 'nom') setErrors((e) => ({ ...e, nom: undefined }))
    if (key === 'siret') setErrors((e) => ({ ...e, siret: undefined }))
  }

  const validate = () => {
    const errs: { nom?: string; siret?: string } = {}
    if (!form.nom.trim()) errs.nom = 'Le nom est requis'
    if (form.siret && form.siret.replace(/\s/g, '').length !== 14) errs.siret = 'SIRET = 14 chiffres'
    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return
    // Nettoyer le SIRET (supprimer espaces)
    const payload = { ...form, siret: form.siret?.replace(/\s/g, '') || undefined }
    try {
      if (sci) {
        await updateSCI.mutateAsync({ id: sci.id, data: payload })
        toast.success('SCI mise à jour')
      } else {
        await createSCI.mutateAsync(payload)
        toast.success('SCI créée')
      }
      onClose()
    } catch {
      toast.error('Erreur lors de la sauvegarde')
    }
  }

  const isPending = createSCI.isPending || updateSCI.isPending

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div>
        <label className={labelClass}>Nom *</label>
        <input
          type="text"
          value={form.nom}
          onChange={(e) => set('nom', e.target.value)}
          className={inputClass}
          placeholder="SCI Mon Patrimoine"
        />
        {errors.nom && <p className="text-[9px] text-[#ef4444] mt-0.5">{errors.nom}</p>}
      </div>

      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className={labelClass}>SIRET (14 chiffres)</label>
          <input
            type="text"
            value={form.siret ?? ''}
            onChange={(e) => set('siret', e.target.value)}
            className={inputClass}
            placeholder="12345678900012"
          />
          {errors.siret && <p className="text-[9px] text-[#ef4444] mt-0.5">{errors.siret}</p>}
        </div>
        <div>
          <label className={labelClass}>Forme juridique</label>
          <select
            value={form.forme_juridique ?? 'SCI'}
            onChange={(e) => set('forme_juridique', e.target.value)}
            className={inputClass}
          >
            <option value="SCI">SCI</option>
            <option value="SARL">SARL</option>
            <option value="SAS">SAS</option>
            <option value="EURL">EURL</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className={labelClass}>Capital (€)</label>
          <input
            type="number"
            value={form.capital ?? ''}
            onChange={(e) => set('capital', Number(e.target.value))}
            className={inputClass}
            placeholder="10000"
          />
        </div>
        <div>
          <label className={labelClass}>Date création</label>
          <input
            type="date"
            value={form.date_creation ?? ''}
            onChange={(e) => set('date_creation', e.target.value)}
            className={inputClass}
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className={labelClass}>Prénom gérant</label>
          <input
            type="text"
            value={form.gerant_prenom ?? ''}
            onChange={(e) => set('gerant_prenom', e.target.value)}
            className={inputClass}
            placeholder="Jean"
          />
        </div>
        <div>
          <label className={labelClass}>Nom gérant</label>
          <input
            type="text"
            value={form.gerant_nom ?? ''}
            onChange={(e) => set('gerant_nom', e.target.value)}
            className={inputClass}
            placeholder="Dupont"
          />
        </div>
      </div>

      <div>
        <label className={labelClass}>Siège social</label>
        <input
          type="text"
          value={form.siege_social ?? ''}
          onChange={(e) => set('siege_social', e.target.value)}
          className={inputClass}
          placeholder="12 Rue de la Paix, 75001 Paris"
        />
      </div>

      <div className="flex gap-2 pt-2">
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
          {isPending ? 'Sauvegarde…' : sci ? 'Mettre à jour' : 'Créer la SCI'}
        </button>
      </div>
    </form>
  )
}
