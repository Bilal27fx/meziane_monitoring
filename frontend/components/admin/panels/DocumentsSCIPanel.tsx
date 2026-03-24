'use client'

import { useRef, useState } from 'react'
import { X, Upload, Trash2, FileText, Paperclip, Download, Eye } from 'lucide-react'
import { useDocumentsSCI, useUploadDocument, useDeleteDocument } from '@/lib/hooks/useAdmin'
import { TYPE_DOCUMENT_LABELS, TYPE_DOCUMENT_SCI } from '@/lib/types'
import type { TypeDocument, Document } from '@/lib/types'
import api from '@/lib/api/client'
import toast from 'react-hot-toast'

interface Props {
  open: boolean
  onClose: () => void
  sciId: number | null
  sciNom?: string
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: '2-digit' })
}

function isPreviewable(nom: string) {
  const ext = nom.toLowerCase()
  return ext.endsWith('.pdf') || ext.endsWith('.jpg') || ext.endsWith('.jpeg') || ext.endsWith('.png')
}

export default function DocumentsSCIPanel({ open, onClose, sciId, sciNom }: Props) {
  const { data: documents = [], isLoading } = useDocumentsSCI(sciId)
  const upload = useUploadDocument()
  const deleteDoc = useDeleteDocument()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [selectedType, setSelectedType] = useState<TypeDocument>('autre')
  const [previewDoc, setPreviewDoc] = useState<Document | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [previewLoading, setPreviewLoading] = useState(false)

  if (!open) return null

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file || !sciId) return
    try {
      await upload.mutateAsync({ sciId, file, typeDocument: selectedType })
      toast.success(`${file.name} uploadé`)
    } catch {
      toast.error("Erreur lors de l'upload")
    }
    e.target.value = ''
  }

  const handleDelete = async (id: number, nom: string) => {
    try {
      await deleteDoc.mutateAsync(id)
      toast.success(`${nom} supprimé`)
      if (previewDoc?.id === id) closePreview()
    } catch {
      toast.error('Erreur lors de la suppression')
    }
  }

  const handleDownload = async (doc: Document) => {
    try {
      const response = await api.get(`/api/documents/${doc.id}/download`, { responseType: 'blob' })
      const url = URL.createObjectURL(response.data as Blob)
      const a = document.createElement('a')
      a.href = url
      a.download = doc.nom_fichier
      a.click()
      URL.revokeObjectURL(url)
    } catch {
      toast.error('Erreur lors du téléchargement')
    }
  }

  const handlePreview = async (doc: Document) => {
    setPreviewDoc(doc)
    setPreviewLoading(true)
    try {
      const response = await api.get(`/api/documents/${doc.id}/preview`, { responseType: 'blob' })
      const url = URL.createObjectURL(response.data as Blob)
      setPreviewUrl(url)
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

  const isImage = (nom: string) => /\.(jpg|jpeg|png)$/i.test(nom)

  return (
    <>
      <div className="fixed inset-0 z-30 bg-black/40" onClick={onClose} />
      <div className="fixed right-0 top-0 bottom-0 z-40 w-[420px] bg-[#111111] border-l border-[#262626] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-[#262626]">
          <div>
            <h3 className="text-sm font-semibold text-white">Documents</h3>
            {sciNom && <p className="text-xs text-[#737373] mt-0.5">{sciNom}</p>}
          </div>
          <button onClick={onClose} className="w-7 h-7 flex items-center justify-center rounded text-[#525252] hover:text-white hover:bg-[#262626] transition-colors">
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Preview zone */}
        {previewDoc && (
          <div className="border-b border-[#262626] bg-[#0d0d0d]">
            <div className="flex items-center justify-between px-3 py-2">
              <span className="text-[10px] text-[#737373] truncate flex-1">{previewDoc.nom_fichier}</span>
              <div className="flex items-center gap-1 ml-2">
                <button
                  onClick={() => handleDownload(previewDoc)}
                  className="flex items-center gap-1 px-2 py-1 text-[9px] text-[#737373] hover:text-white hover:bg-[#262626] rounded transition-colors"
                >
                  <Download className="h-3 w-3" />
                  Télécharger
                </button>
                <button onClick={closePreview} className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-white hover:bg-[#262626] transition-colors">
                  <X className="h-3 w-3" />
                </button>
              </div>
            </div>
            <div className="px-3 pb-3" style={{ height: '280px' }}>
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

        {/* Upload zone */}
        <div className="px-4 py-3 border-b border-[#262626] space-y-2">
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value as TypeDocument)}
            className="w-full h-8 text-xs bg-[#0d0d0d] border border-[#262626] rounded px-2.5 text-white focus:outline-none"
          >
            {TYPE_DOCUMENT_SCI.map((t) => (
              <option key={t} value={t}>{TYPE_DOCUMENT_LABELS[t]}</option>
            ))}
          </select>
          <input ref={fileInputRef} type="file" className="hidden" accept=".pdf,.jpg,.jpeg,.png" onChange={handleFileSelect} />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={upload.isPending}
            className="w-full h-8 flex items-center justify-center gap-1.5 border border-dashed border-[#262626] rounded text-xs text-[#737373] hover:border-[#404040] hover:text-white transition-colors disabled:opacity-50"
          >
            <Upload className="h-3.5 w-3.5" />
            {upload.isPending ? 'Upload…' : 'Ajouter un document'}
          </button>
        </div>

        {/* List */}
        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="p-4 space-y-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="h-12 bg-[#262626]/30 rounded animate-pulse" />
              ))}
            </div>
          ) : documents.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center px-6">
              <FileText className="h-8 w-8 text-[#262626] mb-2" />
              <p className="text-xs text-[#525252]">Aucun document pour cette SCI</p>
            </div>
          ) : (
            <ul className="divide-y divide-[#262626]/50">
              {documents.map((doc) => (
                <li
                  key={doc.id}
                  className={`flex items-center gap-2 px-4 py-3 transition-colors ${previewDoc?.id === doc.id ? 'bg-[#1a1a1a]' : 'hover:bg-[#161616]'}`}
                >
                  <Paperclip className="h-3.5 w-3.5 text-[#525252] shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-white truncate">{doc.nom_fichier}</p>
                    <p className="text-[9px] text-[#525252]">
                      {TYPE_DOCUMENT_LABELS[doc.type_document]} · {formatDate(doc.uploaded_at)}
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
                    <button
                      onClick={() => handleDownload(doc)}
                      className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-white hover:bg-[#262626] transition-colors"
                      title="Télécharger"
                    >
                      <Download className="h-3 w-3" />
                    </button>
                    <button
                      onClick={() => handleDelete(doc.id, doc.nom_fichier)}
                      className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-[#ef4444] hover:bg-[#ef4444]/10 transition-colors"
                      title="Supprimer"
                    >
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
