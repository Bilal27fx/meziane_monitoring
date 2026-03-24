'use client'

import { useState, useRef } from 'react'
import { Upload, X, Paperclip } from 'lucide-react'
import { useCreateLocataire, useUpdateLocataire, useBiens } from '@/lib/hooks/useAdmin'
import api from '@/lib/api/client'
import toast from 'react-hot-toast'
import type { Locataire, LocataireFormData, BailFormData, TypeDocument } from '@/lib/types'
import { TYPE_DOCUMENT_LABELS } from '@/lib/types'

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

  const existingBail = locataire?.bail

  const [form, setForm] = useState<LocataireFormData>({
    prenom: locataire?.prenom ?? '',
    nom: locataire?.nom ?? '',
    email: locataire?.email ?? '',
    telephone: locataire?.telephone ?? '',
    date_naissance: locataire?.date_naissance ?? '',
    profession: locataire?.profession ?? '',
    revenus_annuels: locataire?.revenus_annuels ?? undefined,
    bail: existingBail ? {
      bien_id: existingBail.bien_id,
      date_debut: existingBail.date_debut,
      date_fin: existingBail.date_fin ?? '',
      loyer_mensuel: existingBail.loyer_mensuel,
      charges_mensuelles: existingBail.charges_mensuelles,
      depot_garantie: existingBail.depot_garantie,
    } : undefined,
  })

  const [hasBail, setHasBail] = useState(!!existingBail)
  const [pendingFiles, setPendingFiles] = useState<Array<{ file: File; type: TypeDocument }>>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  const set = <K extends keyof LocataireFormData>(key: K, value: LocataireFormData[K]) => {
    setForm((f) => ({ ...f, [key]: value }))
  }

  const setBail = <K extends keyof BailFormData>(key: K, value: BailFormData[K]) => {
    setForm((f) => ({
      ...f,
      bail: { ...(f.bail ?? { bien_id: 0, date_debut: '', loyer_mensuel: 0, charges_mensuelles: 0 }), [key]: value },
    }))
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files ?? [])
    const newEntries = files.map((file) => ({ file, type: 'autre' as TypeDocument }))
    setPendingFiles((prev) => [...prev, ...newEntries])
    e.target.value = ''
  }

  const removeFile = (index: number) => {
    setPendingFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const updateFileType = (index: number, type: TypeDocument) => {
    setPendingFiles((prev) => prev.map((entry, i) => i === index ? { ...entry, type } : entry))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const bail = hasBail && form.bail
      ? { ...form.bail, date_fin: form.bail.date_fin || null }
      : undefined
    const payload: LocataireFormData = {
      ...form,
      telephone: form.telephone || null,
      date_naissance: form.date_naissance || null,
      profession: form.profession || null,
      bail,
    }
    try {
      let locataireId: number
      if (locataire) {
        await updateLocataire.mutateAsync({ id: locataire.id, data: payload })
        locataireId = locataire.id
        toast.success('Locataire mis à jour')
      } else {
        const res = await createLocataire.mutateAsync(payload)
        locataireId = (res.data as { id: number }).id
        toast.success('Locataire créé')
      }
      // Upload des documents en attente
      for (const { file, type } of pendingFiles) {
        const fd = new FormData()
        fd.append('locataire_id', String(locataireId))
        fd.append('type_document', type)
        fd.append('file', file)
        await api.post('/api/documents/upload-locataire', fd, { headers: { 'Content-Type': undefined } })
      }
      onClose()
    } catch {
      toast.error('Erreur lors de la sauvegarde')
    }
  }

  const isPending = createLocataire.isPending || updateLocataire.isPending
  const bail = form.bail

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
      <div className="flex items-center gap-2 mt-4">
        <p className={sectionClass + ' flex-1 mb-0 border-0'}>Bail</p>
        <label className="flex items-center gap-1.5 text-[9px] text-[#525252] cursor-pointer">
          <input
            type="checkbox"
            checked={hasBail}
            onChange={(e) => {
              setHasBail(e.target.checked)
              if (e.target.checked && !form.bail) {
                setForm((f) => ({ ...f, bail: { bien_id: 0, date_debut: '', loyer_mensuel: 0, charges_mensuelles: 0 } }))
              }
            }}
            className="accent-white"
          />
          Associer un bail
        </label>
      </div>
      <div className="border-b border-[#262626] mb-2" />

      {hasBail && (
        <>
          <div>
            <label className={labelClass}>Bien *</label>
            <select
              value={bail?.bien_id ?? ''}
              onChange={(e) => setBail('bien_id', Number(e.target.value))}
              className={inputClass}
              required={hasBail}
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
                value={bail?.date_debut ?? ''}
                onChange={(e) => setBail('date_debut', e.target.value)}
                className={inputClass}
                required={hasBail}
              />
            </div>
            <div>
              <label className={labelClass}>Date fin</label>
              <input
                type="date"
                value={bail?.date_fin ?? ''}
                onChange={(e) => setBail('date_fin', e.target.value)}
                className={inputClass}
              />
            </div>
            <div>
              <label className={labelClass}>Loyer (€) *</label>
              <input
                type="number"
                value={bail?.loyer_mensuel ?? ''}
                onChange={(e) => setBail('loyer_mensuel', Number(e.target.value))}
                className={inputClass}
                required={hasBail}
                placeholder="1200"
              />
            </div>
            <div>
              <label className={labelClass}>Charges (€)</label>
              <input
                type="number"
                value={bail?.charges_mensuelles ?? ''}
                onChange={(e) => setBail('charges_mensuelles', Number(e.target.value))}
                className={inputClass}
                placeholder="150"
              />
            </div>
            <div>
              <label className={labelClass}>Dépôt garantie (€)</label>
              <input
                type="number"
                value={bail?.depot_garantie ?? ''}
                onChange={(e) => setBail('depot_garantie', Number(e.target.value) || undefined)}
                className={inputClass}
                placeholder="2400"
              />
            </div>
          </div>
        </>
      )}

      {/* Documents */}
      <p className={sectionClass}>Documents</p>
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept=".pdf,.jpg,.jpeg,.png"
        className="hidden"
        onChange={handleFileSelect}
      />
      <div
        onClick={() => fileInputRef.current?.click()}
        className="border-2 border-dashed border-[#262626] rounded-md p-6 text-center hover:border-[#404040] transition-colors cursor-pointer"
      >
        <Upload className="h-6 w-6 text-[#404040] mx-auto mb-2" />
        <p className="text-xs text-[#737373]">Cliquer pour ajouter des documents</p>
        <p className="text-[9px] text-[#525252] mt-0.5">PDF, JPG, PNG — max 10MB</p>
      </div>
      {pendingFiles.length > 0 && (
        <div className="space-y-1.5 mt-1">
          {pendingFiles.map((entry, i) => (
            <div key={i} className="flex items-center gap-2 p-2 bg-[#1a1a1a] rounded border border-[#262626]">
              <Paperclip className="h-3 w-3 text-[#525252] shrink-0" />
              <span className="text-[10px] text-[#737373] truncate flex-1">{entry.file.name}</span>
              <select
                value={entry.type}
                onChange={(e) => updateFileType(i, e.target.value as TypeDocument)}
                className="h-6 text-[10px] bg-[#0d0d0d] border border-[#262626] rounded px-1 text-[#737373] focus:outline-none"
              >
                {(Object.keys(TYPE_DOCUMENT_LABELS) as TypeDocument[]).map((t) => (
                  <option key={t} value={t}>{TYPE_DOCUMENT_LABELS[t]}</option>
                ))}
              </select>
              <button
                type="button"
                onClick={() => removeFile(i)}
                className="text-[#525252] hover:text-white transition-colors"
              >
                <X className="h-3 w-3" />
              </button>
            </div>
          ))}
        </div>
      )}

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
