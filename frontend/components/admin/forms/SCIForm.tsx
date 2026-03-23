'use client'

import { useState } from 'react'
import { useCreateSCI, useUpdateSCI } from '@/lib/hooks/useAdmin'
import { useAppStore } from '@/lib/stores/app-store'
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
    capital_social: sci?.capital_social ?? undefined,
    adresse_siege: sci?.adresse_siege ?? '',
    date_creation: sci?.date_creation ?? '',
    email: sci?.email ?? '',
  })

  const [errors, setErrors] = useState<{ nom?: string }>({})

  const set = (key: keyof SCIFormData, value: string | number) => {
    setForm((f) => ({ ...f, [key]: value }))
    if (key === 'nom') setErrors((e) => ({ ...e, nom: undefined }))
  }

  const validate = () => {
    const errs: { nom?: string } = {}
    if (!form.nom.trim()) errs.nom = 'Le nom est requis'
    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return

    try {
      if (sci) {
        await updateSCI.mutateAsync({ id: sci.id, data: form })
        toast.success('SCI mise à jour')
      } else {
        await createSCI.mutateAsync(form)
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
          <label className={labelClass}>SIRET</label>
          <input
            type="text"
            value={form.siret ?? ''}
            onChange={(e) => set('siret', e.target.value)}
            className={inputClass}
            placeholder="123 456 789 00012"
          />
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
          <label className={labelClass}>Capital social (€)</label>
          <input
            type="number"
            value={form.capital_social ?? ''}
            onChange={(e) => set('capital_social', Number(e.target.value))}
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

      <div>
        <label className={labelClass}>Adresse siège</label>
        <input
          type="text"
          value={form.adresse_siege ?? ''}
          onChange={(e) => set('adresse_siege', e.target.value)}
          className={inputClass}
          placeholder="12 Rue de la Paix, 75001 Paris"
        />
      </div>

      <div>
        <label className={labelClass}>Email</label>
        <input
          type="email"
          value={form.email ?? ''}
          onChange={(e) => set('email', e.target.value)}
          className={inputClass}
          placeholder="contact@sci.fr"
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
