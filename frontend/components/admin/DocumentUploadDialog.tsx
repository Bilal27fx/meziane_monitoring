'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { documentsApi, TypeDocument, DOCUMENT_TYPE_LABELS, SCI_DOCUMENT_TYPES, BIEN_DOCUMENT_TYPES, LOCATAIRE_DOCUMENT_TYPES } from '@/lib/api/documents'
import { toast } from 'sonner'
import { Upload, File as FileIcon } from 'lucide-react'

const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

const documentUploadSchema = z.object({
  type_document: z.nativeEnum(TypeDocument, {
    required_error: 'Le type de document est requis',
  }),
  file: z.any()
    .refine((file) => file && file instanceof File, 'Le fichier est requis')
    .refine((file) => file && file.size <= MAX_FILE_SIZE, 'Le fichier ne doit pas dépasser 10MB'),
  date_document: z.string().optional(),
})

type DocumentUploadFormData = z.infer<typeof documentUploadSchema>

interface DocumentUploadDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  sciId: number
  bienId?: number
  locataireId?: number
  onSuccess: () => void
}

export function DocumentUploadDialog({
  open,
  onOpenChange,
  sciId,
  bienId,
  locataireId,
  onSuccess,
}: DocumentUploadDialogProps) {
  const [isUploading, setIsUploading] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
    watch,
  } = useForm<DocumentUploadFormData>({
    resolver: zodResolver(documentUploadSchema),
  })

  const typeDocument = watch('type_document')
  const documentTypes = locataireId ? LOCATAIRE_DOCUMENT_TYPES : bienId ? BIEN_DOCUMENT_TYPES : SCI_DOCUMENT_TYPES

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setValue('file', file, { shouldValidate: true })
    }
  }

  const onSubmit = async (data: DocumentUploadFormData) => {
    if (!selectedFile) {
      toast.error('Veuillez sélectionner un fichier')
      return
    }

    try {
      setIsUploading(true)

      await documentsApi.upload({
        sci_id: sciId,
        type_document: data.type_document,
        file: selectedFile,
        bien_id: bienId,
        locataire_id: locataireId,
        date_document: data.date_document || undefined,
      })

      toast.success('Document téléchargé avec succès')
      reset()
      setSelectedFile(null)
      onOpenChange(false)
      onSuccess()
    } catch (error: any) {
      console.error('Error uploading document:', error)
      toast.error(error.response?.data?.detail || 'Erreur lors du téléchargement')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Télécharger un document</DialogTitle>
          <DialogDescription>
            {locataireId
              ? 'Ajoutez un document pour ce locataire (Pièce d\'identité, Contrat de travail, etc.)'
              : bienId
              ? 'Ajoutez un document pour ce bien (Bail, DPE, Diagnostics, etc.)'
              : 'Ajoutez un document pour cette SCI (KBIS, Statuts, Relevés, etc.)'}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="space-y-4">
            {/* Type de document */}
            <div className="space-y-2">
              <Label htmlFor="type_document">
                Type de document <span className="text-destructive">*</span>
              </Label>
              <Select
                onValueChange={(value) => setValue('type_document', value as TypeDocument, { shouldValidate: true })}
                value={typeDocument}
              >
                <SelectTrigger className={errors.type_document ? 'border-destructive' : ''}>
                  <SelectValue placeholder="Sélectionnez un type" />
                </SelectTrigger>
                <SelectContent>
                  {documentTypes.map((type) => (
                    <SelectItem key={type} value={type}>
                      {DOCUMENT_TYPE_LABELS[type]}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.type_document && (
                <p className="text-sm text-destructive">{errors.type_document.message}</p>
              )}
            </div>

            {/* Date du document */}
            <div className="space-y-2">
              <Label htmlFor="date_document">Date du document (optionnel)</Label>
              <Input
                id="date_document"
                type="date"
                {...register('date_document')}
              />
            </div>

            {/* Upload fichier */}
            <div className="space-y-2">
              <Label htmlFor="file">
                Fichier <span className="text-destructive">*</span>
              </Label>
              <div className="flex items-center gap-3">
                <Input
                  id="file"
                  type="file"
                  onChange={handleFileChange}
                  accept=".pdf,.jpg,.jpeg,.png,.doc,.docx,.xls,.xlsx"
                  className={errors.file ? 'border-destructive' : ''}
                />
              </div>
              {errors.file && (
                <p className="text-sm text-destructive">{errors.file.message as string}</p>
              )}
              {selectedFile && (
                <div className="flex items-center gap-2 rounded-lg border border-border bg-secondary/30 p-3">
                  <FileIcon className="h-4 w-4 text-muted-foreground" />
                  <div className="flex-1 min-w-0">
                    <p className="truncate text-sm font-medium">{selectedFile.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
              )}
              <p className="text-xs text-muted-foreground">
                Formats acceptés: PDF, JPG, PNG, DOC, DOCX, XLS, XLSX (max 10MB)
              </p>
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                reset()
                setSelectedFile(null)
                onOpenChange(false)
              }}
              disabled={isUploading}
            >
              Annuler
            </Button>
            <Button type="submit" disabled={isUploading || !selectedFile}>
              {isUploading ? (
                <>
                  <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-primary-foreground border-t-transparent" />
                  Téléchargement...
                </>
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" />
                  Télécharger
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
