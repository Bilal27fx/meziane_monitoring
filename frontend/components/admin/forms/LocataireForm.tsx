'use client'

import { useState } from 'react'
import { X, Paperclip, Folder } from 'lucide-react'
import {
  useCreateLocataire,
  useUpdateLocataire,
  useBiens,
  useUploadDocument,
  useCreateDocumentFolder,
  useDocumentLibrary,
} from '@/lib/hooks/useAdmin'
import toast from 'react-hot-toast'
import type { Locataire, LocataireFormData, BailFormData, DocumentFolder } from '@/lib/types'
import DocumentActionComposer from '@/components/admin/documents/DocumentActionComposer'

interface Props {
  locataire?: Locataire
  onClose: () => void
}

const inputClass = 'w-full h-8 text-xs bg-[#0d0d0d] border border-[#262626] rounded px-2.5 text-white focus:outline-none focus:border-[#404040] transition-colors'
const labelClass = 'text-[9px] text-[#525252] uppercase tracking-wide block mb-1'
const sectionClass = 'text-[10px] text-[#737373] uppercase tracking-widest mb-2 mt-4 first:mt-0 pb-1 border-b border-[#262626]'

type PendingFolder = {
  temp_id: string
  nom: string
}

type PendingDocument = {
  temp_id: string
  file: File
  nom_document: string
  folder_ref: string
}

export default function LocataireForm({ locataire, onClose }: Props) {
  const createLocataire = useCreateLocataire()
  const updateLocataire = useUpdateLocataire()
  const uploadDocument = useUploadDocument()
  const createFolder = useCreateDocumentFolder()
  const { data: biensData } = useBiens()
  const biens = biensData?.items ?? []
  const documentLibrary = useDocumentLibrary({ locataireId: locataire?.id })
  const existingFolders = documentLibrary.data?.folders ?? []

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
  const [pendingFolders, setPendingFolders] = useState<PendingFolder[]>([])
  const [pendingDocuments, setPendingDocuments] = useState<PendingDocument[]>([])

  const set = <K extends keyof LocataireFormData>(key: K, value: LocataireFormData[K]) => {
    setForm((f) => ({ ...f, [key]: value }))
  }

  const setBail = <K extends keyof BailFormData>(key: K, value: BailFormData[K]) => {
    setForm((f) => ({
      ...f,
      bail: { ...(f.bail ?? { bien_id: 0, date_debut: '', loyer_mensuel: 0, charges_mensuelles: 0 }), [key]: value },
    }))
  }

  const handleQueueFolder = async (folderName: string) => {
    setPendingFolders((prev) => [
      ...prev,
      { temp_id: `pending-folder-${Date.now()}-${prev.length}`, nom: folderName },
    ])
  }

  const handleQueueDocument = async ({
    folderRef,
    documentName,
    files,
  }: {
    folderRef: string
    documentName: string
    files: File[]
  }) => {
    setPendingDocuments((prev) => [
      ...prev,
      ...files.map((file, index) => ({
        temp_id: `pending-document-${Date.now()}-${prev.length + index}`,
        file,
        nom_document: documentName && index === 0 ? documentName : file.name,
        folder_ref: folderRef,
      })),
    ])
  }

  const removePendingFolder = (tempId: string) => {
    setPendingFolders((prev) => prev.filter((folder) => folder.temp_id !== tempId))
    setPendingDocuments((prev) =>
      prev.map((document) =>
        document.folder_ref === tempId ? { ...document, folder_ref: '' } : document
      )
    )
  }

  const removePendingDocument = (tempId: string) => {
    setPendingDocuments((prev) => prev.filter((document) => document.temp_id !== tempId))
  }

  const getFolderLabel = (folderRef: string) => {
    if (!folderRef) return 'Racine'
    const pendingFolder = pendingFolders.find((folder) => folder.temp_id === folderRef)
    if (pendingFolder) return `${pendingFolder.nom} (à créer)`
    const existingFolder = existingFolders.find((folder) => String(folder.id) === folderRef)
    return existingFolder?.nom ?? 'Dossier'
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

      const createdFolderIds = new Map<string, number>()
      for (const folder of pendingFolders) {
        const response = await createFolder.mutateAsync({
          locataireId,
          nom: folder.nom,
        })
        createdFolderIds.set(folder.temp_id, response.data.id)
      }

      for (const document of pendingDocuments) {
        const folderId = document.folder_ref.startsWith('pending-folder-')
          ? createdFolderIds.get(document.folder_ref)
          : document.folder_ref
            ? Number(document.folder_ref)
            : undefined

        await uploadDocument.mutateAsync({
          locataireId,
          folderId,
          file: document.file,
          nomDocument: document.nom_document,
        })
      }
      onClose()
    } catch {
      toast.error('Erreur lors de la sauvegarde')
    }
  }

  const isPending = (
    createLocataire.isPending
    || updateLocataire.isPending
    || uploadDocument.isPending
    || createFolder.isPending
  )
  const bail = form.bail
  const folderChoices: Array<{ value: string; label: string }> = [
    { value: '', label: 'Racine' },
    ...existingFolders.map((folder: DocumentFolder) => ({
      value: String(folder.id),
      label: folder.nom,
    })),
    ...pendingFolders.map((folder) => ({
      value: folder.temp_id,
      label: `${folder.nom} (à créer)`,
    })),
  ]

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
      <DocumentActionComposer
        folderOptions={folderChoices}
        defaultFolderRef=""
        isBusy={isPending}
        onCreateFolder={handleQueueFolder}
        onUploadDocument={handleQueueDocument}
      />

      {(pendingFolders.length > 0 || pendingDocuments.length > 0) && (
        <div className="space-y-2 mt-1">
          {pendingFolders.map((folder) => (
            <div key={folder.temp_id} className="flex items-center gap-2 p-2 bg-[#1a1a1a] rounded border border-[#262626]">
              <Folder className="h-3 w-3 text-[#eab308] shrink-0" />
              <div className="min-w-0 flex-1">
                <p className="text-[10px] text-white truncate">{folder.nom}</p>
                <p className="text-[9px] text-[#525252]">Dossier à créer</p>
              </div>
              <button
                type="button"
                onClick={() => removePendingFolder(folder.temp_id)}
                className="text-[#525252] hover:text-white transition-colors"
              >
                <X className="h-3 w-3" />
              </button>
            </div>
          ))}
          {pendingDocuments.map((document) => (
            <div key={document.temp_id} className="flex items-center gap-2 p-2 bg-[#1a1a1a] rounded border border-[#262626]">
              <Paperclip className="h-3 w-3 text-[#525252] shrink-0" />
              <div className="min-w-0 flex-1">
                <p className="text-[10px] text-white truncate">{document.nom_document}</p>
                <p className="text-[9px] text-[#525252]">
                  {getFolderLabel(document.folder_ref)}
                </p>
              </div>
              <button
                type="button"
                onClick={() => removePendingDocument(document.temp_id)}
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
