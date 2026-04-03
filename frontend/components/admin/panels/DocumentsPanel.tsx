'use client'

import { useEffect, useState } from 'react'
import { X, Trash2, FileText, Paperclip, Download, Eye, Folder, ChevronLeft } from 'lucide-react'
import {
  useDocumentLibrary,
  useUploadDocument,
  useDeleteDocument,
  useCreateDocumentFolder,
  useDeleteDocumentFolder,
} from '@/lib/hooks/useAdmin'
import type { Document, DocumentFolder } from '@/lib/types'
import api from '@/lib/api/client'
import toast from 'react-hot-toast'
import DocumentActionComposer from '@/components/admin/documents/DocumentActionComposer'

export type DocumentEntityType = 'sci' | 'bien' | 'locataire'

interface Props {
  open: boolean
  onClose: () => void
  entityType: DocumentEntityType
  entityId: number | null
  entityNom?: string
  /** Requis pour bien : sci_id du bien */
  sciId?: number
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: '2-digit' })
}

function isPreviewable(nom: string) {
  return /\.(pdf|jpg|jpeg|png)$/i.test(nom)
}

function isImage(nom: string) {
  return /\.(jpg|jpeg|png)$/i.test(nom)
}

export default function DocumentsPanel({ open, onClose, entityType, entityId, entityNom, sciId }: Props) {
  const [currentFolder, setCurrentFolder] = useState<DocumentFolder | null>(null)
  const [folderTrail, setFolderTrail] = useState<DocumentFolder[]>([])
  const uploadDoc = useUploadDocument()
  const deleteDoc = useDeleteDocument()
  const createFolder = useCreateDocumentFolder()
  const deleteFolder = useDeleteDocumentFolder()
  const [previewDoc, setPreviewDoc] = useState<Document | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [previewLoading, setPreviewLoading] = useState(false)

  const library = useDocumentLibrary({
    sciId: entityType === 'sci' ? entityId : sciId,
    bienId: entityType === 'bien' ? entityId : undefined,
    locataireId: entityType === 'locataire' ? entityId : undefined,
    folderId: currentFolder?.id,
  })
  const folders = library.data?.folders ?? []
  const documents = library.data?.documents ?? []
  const isLoading = library.isLoading

  useEffect(() => {
    if (!open) return
    setCurrentFolder(null)
    setFolderTrail([])
  }, [open, entityId, entityType])

  if (!open) return null

  const isPending = uploadDoc.isPending || createFolder.isPending

  const handleDelete = async (id: number, nom: string) => {
    try {
      await deleteDoc.mutateAsync(id)
      toast.success(`${nom} supprimé`)
      if (previewDoc?.id === id) closePreview()
    } catch {
      toast.error('Erreur lors de la suppression')
    }
  }

  const handleCreateFolderFromComposer = async (folderName: string) => {
    if (!entityId) return
    try {
      const response = await createFolder.mutateAsync({
        sciId: entityType === 'sci' ? entityId : sciId,
        bienId: entityType === 'bien' ? entityId : undefined,
        locataireId: entityType === 'locataire' ? entityId : undefined,
        parentId: currentFolder?.id,
        nom: folderName,
      })
      const createdFolder = response.data
      toast.success(`Dossier "${createdFolder.nom}" créé`)
    } catch {
      toast.error('Erreur lors de la création du dossier')
      throw new Error('document-folder-create-failed')
    }
  }

  const handleUploadFromComposer = async ({
    folderRef,
    documentName,
    files,
  }: {
    folderRef: string
    documentName: string
    files: File[]
  }) => {
    if (!entityId) return
    const parsedFolderId = folderRef ? Number(folderRef) : undefined
    try {
      for (const [index, file] of files.entries()) {
        await uploadDoc.mutateAsync({
          sciId: entityType === 'sci' ? entityId : sciId,
          bienId: entityType === 'bien' ? entityId : undefined,
          locataireId: entityType === 'locataire' ? entityId : undefined,
          folderId: parsedFolderId,
          file,
          nomDocument: index === 0 ? documentName || undefined : undefined,
        })
      }
      toast.success(
        files.length === 1
          ? `${documentName || files[0].name} uploadé`
          : `${files.length} documents uploadés`
      )
    } catch {
      toast.error("Erreur lors de l'upload")
      throw new Error('document-upload-failed')
    }
  }

  const handleDeleteFolder = async (folder: DocumentFolder) => {
    try {
      await deleteFolder.mutateAsync(folder.id)
      toast.success(`Dossier "${folder.nom}" supprimé`)
      if (currentFolder?.id === folder.id) {
        setCurrentFolder(null)
        setFolderTrail([])
      }
    } catch {
      toast.error('Le dossier doit être vide avant suppression')
    }
  }

  const openFolder = (folder: DocumentFolder) => {
    setCurrentFolder(folder)
    setFolderTrail((prev) => [...prev, folder])
  }

  const goBackFolder = () => {
    setFolderTrail((prev) => {
      const next = prev.slice(0, -1)
      setCurrentFolder(next[next.length - 1] ?? null)
      return next
    })
  }

  const handleDownload = async (doc: Document) => {
    try {
      const response = await api.get(`/api/documents/${doc.id}/download`, { responseType: 'blob' })
      const blob = response.data instanceof Blob
        ? response.data
        : new Blob([response.data], { type: response.headers['content-type'] ?? 'application/octet-stream' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = doc.nom_fichier || `document-${doc.id}`
      a.style.display = 'none'
      document.body.appendChild(a)
      a.click()
      window.setTimeout(() => {
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
      }, 1000)
    } catch {
      toast.error('Erreur lors du téléchargement')
    }
  }

  const handlePreview = async (doc: Document) => {
    setPreviewDoc(doc)
    setPreviewLoading(true)
    try {
      const response = await api.get(`/api/documents/${doc.id}/preview`, { responseType: 'blob' })
      setPreviewUrl(URL.createObjectURL(response.data as Blob))
    } catch {
      toast.error('Impossible de prévisualiser ce fichier')
      setPreviewDoc(null)
    } finally {
      setPreviewLoading(false)
    }
  }

  const closePreview = () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl)
    setPreviewDoc(null)
    setPreviewUrl(null)
  }

  const TITLES: Record<DocumentEntityType, string> = {
    sci: 'Documents SCI',
    bien: 'Documents du bien',
    locataire: 'Documents locataire',
  }

  const destinationFolders = [
    { value: '', label: 'Racine' },
    ...(currentFolder ? [{ value: String(currentFolder.id), label: `${currentFolder.nom} (courant)` }] : []),
    ...folders
      .filter((folder) => folder.id !== currentFolder?.id)
      .map((folder) => ({ value: String(folder.id), label: folder.nom })),
  ]

  return (
    <>
      <div className="fixed inset-0 z-30 bg-black/40" onClick={onClose} />
      <div className="fixed right-0 top-0 bottom-0 z-40 w-[420px] bg-[#111111] border-l border-[#262626] flex flex-col">

        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-[#262626]">
          <div>
            <h3 className="text-sm font-semibold text-white">{TITLES[entityType]}</h3>
            {entityNom && <p className="text-xs text-[#737373] mt-0.5">{entityNom}</p>}
          </div>
          <button onClick={onClose} className="w-7 h-7 flex items-center justify-center rounded text-[#525252] hover:text-white hover:bg-[#262626] transition-colors">
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Preview */}
        {previewDoc && (
          <div className="border-b border-[#262626] bg-[#0d0d0d]">
            <div className="flex items-center justify-between px-3 py-2">
              <span className="text-[10px] text-[#737373] truncate flex-1">{previewDoc.nom_fichier}</span>
              <div className="flex items-center gap-1 ml-2 shrink-0">
                <button onClick={() => handleDownload(previewDoc)} className="flex items-center gap-1 px-2 py-1 text-[9px] text-[#737373] hover:text-white hover:bg-[#262626] rounded transition-colors">
                  <Download className="h-3 w-3" />
                  Télécharger
                </button>
                <button onClick={closePreview} className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-white hover:bg-[#262626] transition-colors">
                  <X className="h-3 w-3" />
                </button>
              </div>
            </div>
            <div className="px-3 pb-3 h-[260px]">
              {previewLoading ? (
                <div className="h-full bg-[#1a1a1a] rounded animate-pulse" />
              ) : previewUrl ? (
                isImage(previewDoc.nom_fichier) ? (
                  <img src={previewUrl} alt={previewDoc.nom_fichier} className="h-full w-full object-contain rounded" />
                ) : (
                  <iframe src={previewUrl} className="w-full h-full rounded border border-[#262626]" title={previewDoc.nom_fichier} />
                )
              ) : null}
            </div>
          </div>
        )}

        {/* Upload */}
        <div className="px-4 py-3 border-b border-[#262626] space-y-2">
          {currentFolder && (
            <div className="flex items-center gap-2 text-[10px] text-[#737373]">
              <button
                onClick={goBackFolder}
                className="flex items-center gap-1 text-[#737373] hover:text-white transition-colors"
              >
                <ChevronLeft className="h-3 w-3" />
                Retour
              </button>
              <span className="text-[#525252]">/</span>
              <span className="truncate text-white">{currentFolder.nom}</span>
            </div>
          )}
          <DocumentActionComposer
            folderOptions={destinationFolders}
            defaultFolderRef={currentFolder ? String(currentFolder.id) : ''}
            isBusy={isPending}
            onCreateFolder={handleCreateFolderFromComposer}
            onUploadDocument={handleUploadFromComposer}
          />
        </div>

        {/* Liste */}
        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="p-4 space-y-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="h-12 bg-[#262626]/30 rounded animate-pulse" />
              ))}
            </div>
          ) : folders.length === 0 && documents.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center px-6">
              <FileText className="h-8 w-8 text-[#262626] mb-2" />
              <p className="text-xs text-[#525252]">{folders.length === 0 ? 'Aucun document ni dossier' : 'Aucun document dans ce niveau'}</p>
            </div>
          ) : (
            <ul className="divide-y divide-[#262626]/50">
              {folders.map((folder: DocumentFolder) => (
                <li key={`folder-${folder.id}`} className="flex items-center gap-2 px-4 py-3 hover:bg-[#161616] transition-colors">
                  <button
                    onClick={() => openFolder(folder)}
                    className="flex items-center gap-2 flex-1 min-w-0 text-left"
                  >
                    <Folder className="h-3.5 w-3.5 text-[#eab308] shrink-0" />
                    <div className="min-w-0">
                      <p className="text-xs text-white truncate">{folder.nom}</p>
                      <p className="text-[9px] text-[#525252]">Dossier</p>
                    </div>
                  </button>
                  <button
                    onClick={() => handleDeleteFolder(folder)}
                    className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-[#ef4444] hover:bg-[#ef4444]/10 transition-colors"
                    title="Supprimer le dossier"
                  >
                    <Trash2 className="h-3 w-3" />
                  </button>
                </li>
              ))}
              {documents.map((doc: Document) => (
                <li key={doc.id} className={`flex items-center gap-2 px-4 py-3 transition-colors ${previewDoc?.id === doc.id ? 'bg-[#1a1a1a]' : 'hover:bg-[#161616]'}`}>
                  <Paperclip className="h-3.5 w-3.5 text-[#525252] shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-white truncate">{doc.nom_fichier}</p>
                    <p className="text-[9px] text-[#525252]">
                      {formatDate(doc.uploaded_at)}
                    </p>
                  </div>
                  <div className="flex items-center gap-0.5 shrink-0">
                    {isPreviewable(doc.nom_fichier) && (
                      <button
                        onClick={() => previewDoc?.id === doc.id ? closePreview() : handlePreview(doc)}
                        className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-[#3b82f6] hover:bg-[#3b82f6]/10 transition-colors"
                        title="Prévisualiser"
                      >
                        <Eye className="h-3 w-3" />
                      </button>
                    )}
                    <button onClick={() => handleDownload(doc)} className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-white hover:bg-[#262626] transition-colors" title="Télécharger">
                      <Download className="h-3 w-3" />
                    </button>
                    <button onClick={() => handleDelete(doc.id, doc.nom_fichier)} className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-[#ef4444] hover:bg-[#ef4444]/10 transition-colors" title="Supprimer">
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </>
  )
}
