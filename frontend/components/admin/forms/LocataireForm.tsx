'use client'

import { useState } from 'react'
import { Upload } from 'lucide-react'
import { useCreateLocataire, useUpdateLocataire, useBiens } from '@/lib/hooks/useAdmin'
import toast from 'react-hot-toast'
import type { Locataire, LocataireFormData } from '@/lib/types'

interface Props {
  locataire?: Locataire
  onClose: () => void
}

const inputClass = 'w-full h-8 text-xs bg-[#0d0d0d] border border-[#262626] rounded px-2.5 text-white focus:outline-none focus:border-[#404040] transition-colors'
const labelClass = 'text-[9px] text-[#525252] uppercase tracking-wide block mb-1'
const sectionClass = 'text-[10px] text-[#737373] uppercase tracking-widest mb-2 mt-4 first:mt-0 pb-1 border-b border-[#262626]'

export default function LocataireForm({ locataire, onClose }: Props) {
  const createLocataire = useCreateLocataire()
  const updateLocataire = useUpdateLocataire()
  const { data: biensData } = useBiens()
  const biens = biensData?.items ?? []

  const [form, setForm] = useState<LocataireFormData>({
    prenom: locataire?.prenom ?? '',
    nom: locataire?.nom ?? '',
    email: locataire?.email ?? '',
    telephone: locataire?.telephone ?? '',
    date_naissance: locataire?.date_naissance ?? '',
    profession: locataire?.profession ?? '',
    revenus_annuels: locataire?.revenus_annuels ?? undefined,
    bien_id: locataire?.bien_id ?? undefined,
    date_debut: locataire?.bail?.date_debut ?? '',
    date_fin: locataire?.bail?.date_fin ?? '',
    loyer: locataire?.bail?.loyer ?? undefined,
    charges: locataire?.bail?.charges ?? undefined,
    depot_garantie: locataire?.bail?.depot_garantie ?? undefined,
    type_revision: locataire?.bail?.type_revision ?? 'IRL',
  })

  const set = <K extends keyof LocataireFormData>(key: K, value: LocataireFormData[K]) => {
    setForm((f) => ({ ...f, [key]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (locataire) {
        await updateLocataire.mutateAsync({ id: locataire.id, data: form })
        toast.success('Locataire mis à jour')
      } else {
        await createLocataire.mutateAsync(form)
        toast.success('Locataire créé')
      }
      onClose()
    } catch {
      toast.error('Erreur lors de la sauvegarde')
    }
  }

  const isPending = createLocataire.isPending || updateLocataire.isPending

  return (
    <form onSubmit={handleSubmit} className="space-y-2 max-h-[65vh] overflow-y-auto pr-1">
      {/* Identité */}
      <p className={sectionClass}>Identité</p>
      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className={labelClass}>Prénom *</label>
          <input
            type="text"
            value={form.prenom}
            onChange={(e) => set('prenom', e.target.value)}
            className={inputClass}
            required
            placeholder="Jean"
          />
        </div>
        <div>
          <label className={labelClass}>Nom *</label>
          <input
            type="text"
            value={form.nom}
            onChange={(e) => set('nom', e.target.value)}
            className={inputClass}
            required
            placeholder="Dupont"
          />
        </div>
      </div>
      <div>
        <label className={labelClass}>Email *</label>
        <input
          type="email"
          value={form.email}
          onChange={(e) => set('email', e.target.value)}
          className={inputClass}
          required
          placeholder="jean.dupont@email.fr"
        />
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className={labelClass}>Téléphone</label>
          <input
            type="tel"
            value={form.telephone ?? ''}
            onChange={(e) => set('telephone', e.target.value)}
            className={inputClass}
            placeholder="0612345678"
          />
        </div>
        <div>
          <label className={labelClass}>Date naissance</label>
          <input
            type="date"
            value={form.date_naissance ?? ''}
            onChange={(e) => set('date_naissance', e.target.value)}
            className={inputClass}
          />
        </div>
        <div>
          <label className={labelClass}>Profession</label>
          <input
            type="text"
            value={form.profession ?? ''}
            onChange={(e) => set('profession', e.target.value)}
            className={inputClass}
            placeholder="Ingénieur"
          />
        </div>
        <div>
          <label className={labelClass}>Revenus annuels (€)</label>
          <input
            type="number"
            value={form.revenus_annuels ?? ''}
            onChange={(e) => set('revenus_annuels', Number(e.target.value) || undefined)}
            className={inputClass}
            placeholder="45000"
          />
        </div>
      </div>

      {/* Bail */}
      <p className={sectionClass}>Bail</p>
      <div>
        <label className={labelClass}>Bien *</label>
        <select
          value={form.bien_id ?? ''}
          onChange={(e) => set('bien_id', Number(e.target.value) || undefined)}
          className={inputClass}
          required
        >
          <option value="">Sélectionner un bien</option>
          {biens.map((b) => (
            <option key={b.id} value={b.id}>{b.adresse} — {b.ville}</option>
          ))}
        </select>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className={labelClass}>Date début *</label>
          <input
            type="date"
            value={form.date_debut ?? ''}
            onChange={(e) => set('date_debut', e.target.value)}
            className={inputClass}
            required
          />
        </div>
        <div>
          <label className={labelClass}>Date fin</label>
          <input
            type="date"
            value={form.date_fin ?? ''}
            onChange={(e) => set('date_fin', e.target.value)}
            className={inputClass}
          />
        </div>
        <div>
          <label className={labelClass}>Loyer (€) *</label>
          <input
            type="number"
            value={form.loyer ?? ''}
            onChange={(e) => set('loyer', Number(e.target.value) || undefined)}
            className={inputClass}
            required
            placeholder="1200"
          />
        </div>
        <div>
          <label className={labelClass}>Charges (€)</label>
          <input
            type="number"
            value={form.charges ?? ''}
            onChange={(e) => set('charges', Number(e.target.value) || undefined)}
            className={inputClass}
            placeholder="150"
          />
        </div>
        <div>
          <label className={labelClass}>Dépôt garantie (€)</label>
          <input
            type="number"
            value={form.depot_garantie ?? ''}
            onChange={(e) => set('depot_garantie', Number(e.target.value) || undefined)}
            className={inputClass}
            placeholder="2400"
          />
        </div>
        <div>
          <label className={labelClass}>Type révision</label>
          <select
            value={form.type_revision ?? 'IRL'}
            onChange={(e) => set('type_revision', e.target.value)}
            className={inputClass}
          >
            <option value="IRL">IRL</option>
            <option value="ILC">ILC</option>
            <option value="fixe">Fixe</option>
          </select>
        </div>
      </div>

      {/* Documents */}
      <p className={sectionClass}>Documents</p>
      <div className="border-2 border-dashed border-[#262626] rounded-md p-6 text-center hover:border-[#404040] transition-colors cursor-pointer">
        <Upload className="h-6 w-6 text-[#404040] mx-auto mb-2" />
        <p className="text-xs text-[#737373]">Glisser-déposer les documents</p>
        <p className="text-[9px] text-[#525252] mt-0.5">PDF, JPG, PNG — max 10MB</p>
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
          {isPending ? 'Sauvegarde…' : locataire ? 'Mettre à jour' : 'Créer le locataire'}
        </button>
      </div>
    </form>
  )
}
