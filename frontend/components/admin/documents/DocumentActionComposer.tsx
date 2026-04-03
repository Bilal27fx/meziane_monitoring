'use client'

import { useRef, useState } from 'react'
import { FolderPlus, Upload } from 'lucide-react'

type FolderOption = {
  value: string
  label: string
}

type UploadPayload = {
  folderRef: string
  documentName: string
  files: File[]
}

interface Props {
  folderOptions: FolderOption[]
  defaultFolderRef?: string
  isBusy?: boolean
  onCreateFolder: (folderName: string) => void | Promise<void>
  onUploadDocument: (payload: UploadPayload) => void | Promise<void>
}

export default function DocumentActionComposer({
  folderOptions,
  defaultFolderRef = '',
  isBusy = false,
  onCreateFolder,
  onUploadDocument,
}: Props) {
  const [mode, setMode] = useState<'idle' | 'create-folder' | 'upload-document'>('idle')
  const [folderName, setFolderName] = useState('')
  const [documentName, setDocumentName] = useState('')
  const [selectedFolderRef, setSelectedFolderRef] = useState(defaultFolderRef)
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  const reset = () => {
    setMode('idle')
    setFolderName('')
    setDocumentName('')
    setSelectedFolderRef(defaultFolderRef)
    setSelectedFiles([])
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const openCreateFolder = () => {
    setMode('create-folder')
    setFolderName('')
  }

  const openUploadDocument = () => {
    setMode('upload-document')
    setDocumentName('')
    setSelectedFolderRef(defaultFolderRef)
    setSelectedFiles([])
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files ?? [])
    setSelectedFiles(files)
    if (files.length !== 1) setDocumentName('')
  }

  const handleCreateFolder = async () => {
    const trimmedName = folderName.trim()
    if (!trimmedName) return
    await onCreateFolder(trimmedName)
    reset()
  }

  const handleUploadDocument = async () => {
    if (selectedFiles.length === 0) return
    await onUploadDocument({
      folderRef: selectedFolderRef,
      documentName: selectedFiles.length === 1 ? documentName.trim() : '',
      files: selectedFiles,
    })
    reset()
  }

  return (
    <div className="space-y-2">
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.jpg,.jpeg,.png,.csv"
        multiple
        className="hidden"
        onChange={handleFileSelect}
      />

      <div className="grid grid-cols-2 gap-2">
        <button
          type="button"
          onClick={openUploadDocument}
          disabled={isBusy}
          className="h-8 px-3 flex items-center justify-center gap-1.5 text-xs text-[#737373] border border-[#262626] rounded hover:text-white hover:border-[#404040] transition-colors disabled:opacity-50"
        >
          <Upload className="h-3.5 w-3.5" />
          Upload document
        </button>
        <button
          type="button"
          onClick={openCreateFolder}
          disabled={isBusy}
          className="h-8 px-3 flex items-center justify-center gap-1.5 text-xs text-[#737373] border border-[#262626] rounded hover:text-white hover:border-[#404040] transition-colors disabled:opacity-50"
        >
          <FolderPlus className="h-3.5 w-3.5" />
          Créer un dossier
        </button>
      </div>

      {mode === 'create-folder' && (
        <div className="space-y-2 rounded border border-[#262626] bg-[#0d0d0d] p-3">
          <p className="text-[10px] uppercase tracking-widest text-[#737373]">Nom du dossier</p>
          <input
            type="text"
            value={folderName}
            onChange={(e) => setFolderName(e.target.value)}
            placeholder="Ex: Baux 2026"
            className="w-full h-8 text-xs bg-[#111111] border border-[#262626] rounded px-2.5 text-white focus:outline-none"
          />
          <div className="flex gap-2">
            <button
              type="button"
              onClick={reset}
              className="flex-1 h-8 text-xs text-[#737373] border border-[#262626] rounded hover:text-white hover:border-[#404040] transition-colors"
            >
              Annuler
            </button>
            <button
              type="button"
              onClick={handleCreateFolder}
              disabled={!folderName.trim() || isBusy}
              className="flex-1 h-8 text-xs text-white bg-[#1f1f1f] border border-[#404040] rounded hover:bg-[#262626] transition-colors disabled:opacity-50"
            >
              Enregistrer
            </button>
          </div>
        </div>
      )}

      {mode === 'upload-document' && (
        <div className="space-y-2 rounded border border-[#262626] bg-[#0d0d0d] p-3">
          <p className="text-[10px] uppercase tracking-widest text-[#737373]">Uploader un document</p>
          <select
            value={selectedFolderRef}
            onChange={(e) => setSelectedFolderRef(e.target.value)}
            className="w-full h-8 text-xs bg-[#111111] border border-[#262626] rounded px-2.5 text-white focus:outline-none"
          >
            {folderOptions.map((folder) => (
              <option key={folder.value || 'root'} value={folder.value}>
                {folder.label}
              </option>
            ))}
          </select>
          <input
            type="text"
            value={documentName}
            onChange={(e) => setDocumentName(e.target.value)}
            disabled={selectedFiles.length > 1}
            placeholder={selectedFiles.length > 1 ? 'Renommage désactivé pour plusieurs fichiers' : 'Nom du document'}
            className="w-full h-8 text-xs bg-[#111111] border border-[#262626] rounded px-2.5 text-white focus:outline-none"
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="w-full h-8 flex items-center justify-center gap-1.5 border border-dashed border-[#262626] rounded text-xs text-[#737373] hover:border-[#404040] hover:text-white transition-colors"
          >
            <Upload className="h-3.5 w-3.5" />
            {selectedFiles.length === 0
              ? 'Choisir un ou plusieurs fichiers'
              : selectedFiles.length === 1
                ? selectedFiles[0].name
                : `${selectedFiles.length} fichiers sélectionnés`}
          </button>
          {selectedFiles.length > 1 && (
            <div className="rounded border border-[#262626] bg-[#111111] px-2.5 py-2">
              <p className="mb-1 text-[10px] uppercase tracking-widest text-[#525252]">Fichiers</p>
              <ul className="space-y-1">
                {selectedFiles.map((file) => (
                  <li key={`${file.name}-${file.size}-${file.lastModified}`} className="truncate text-[10px] text-[#a3a3a3]">
                    {file.name}
                  </li>
                ))}
              </ul>
            </div>
          )}
          <div className="flex gap-2">
            <button
              type="button"
              onClick={reset}
              className="flex-1 h-8 text-xs text-[#737373] border border-[#262626] rounded hover:text-white hover:border-[#404040] transition-colors"
            >
              Annuler
            </button>
            <button
              type="button"
              onClick={handleUploadDocument}
              disabled={selectedFiles.length === 0 || isBusy}
              className="flex-1 h-8 text-xs text-white bg-[#1f1f1f] border border-[#404040] rounded hover:bg-[#262626] transition-colors disabled:opacity-50"
            >
              {isBusy ? 'En cours…' : 'Enregistrer'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
