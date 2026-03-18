'use client'

import { useEffect, useState } from 'react'
import { Panel } from '@/components/ui/Panel'
import { Button } from '@/components/ui/button'
import { SCIFormDialog } from '@/components/admin/SCIFormDialog'
import { DocumentUploadDialog } from '@/components/admin/DocumentUploadDialog'
import { sciApi, type SCI } from '@/lib/api/sci'
import { documentsApi, type Document, DOCUMENT_TYPE_LABELS } from '@/lib/api/documents'
import { Plus, Building, Pencil, Trash2, MapPin, Users, Euro, FileText, Upload as UploadIcon, Download, X } from 'lucide-react'
import { toast } from 'sonner'
import { formatCurrency, formatDate } from '@/lib/utils/format'

export default function SCIPage() {
  const [scis, setScis] = useState<SCI[]>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [documentDialogOpen, setDocumentDialogOpen] = useState(false)
  const [selectedSCI, setSelectedSCI] = useState<SCI | undefined>()
  const [selectedSCIForDocs, setSelectedSCIForDocs] = useState<SCI | undefined>()
  const [documents, setDocuments] = useState<Record<number, Document[]>>({})

  const loadSCIs = async () => {
    try {
      setLoading(true)
      const data = await sciApi.getAll()
      setScis(data)

      // Load documents for each SCI
      const docsMap: Record<number, Document[]> = {}
      await Promise.all(
        data.map(async (sci) => {
          try {
            const docs = await documentsApi.getBySCI(sci.id)
            docsMap[sci.id] = docs
          } catch (error) {
            docsMap[sci.id] = []
          }
        })
      )
      setDocuments(docsMap)
    } catch (error) {
      console.error('Error loading SCIs:', error)
      toast.error('Erreur lors du chargement des SCI')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSCIs()
  }, [])

  const handleAdd = () => {
    setSelectedSCI(undefined)
    setDialogOpen(true)
  }

  const handleEdit = (sci: SCI) => {
    setSelectedSCI(sci)
    setDialogOpen(true)
  }

  const handleDelete = async (sci: SCI) => {
    if (!confirm(`Êtes-vous sûr de vouloir supprimer la SCI "${sci.nom}" ?`)) {
      return
    }

    try {
      await sciApi.delete(sci.id)
      toast.success('SCI supprimée avec succès')
      loadSCIs()
    } catch (error: any) {
      console.error('Error deleting SCI:', error)
      toast.error(error.response?.data?.detail || 'Erreur lors de la suppression')
    }
  }

  const handleUploadDocument = (sci: SCI) => {
    setSelectedSCIForDocs(sci)
    setDocumentDialogOpen(true)
  }

  const handleDeleteDocument = async (documentId: number) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce document ?')) {
      return
    }

    try {
      await documentsApi.delete(documentId)
      toast.success('Document supprimé avec succès')
      loadSCIs()
    } catch (error: any) {
      console.error('Error deleting document:', error)
      toast.error(error.response?.data?.detail || 'Erreur lors de la suppression')
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="text-center">
          <div className="mb-4 h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent mx-auto"></div>
          <p className="text-sm text-muted-foreground">Chargement des SCI...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">SCI</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Gérez vos sociétés civiles immobilières
          </p>
        </div>
        <Button onClick={handleAdd} className="gap-2">
          <Plus className="h-4 w-4" />
          Ajouter une SCI
        </Button>
      </div>

      {scis.length === 0 ? (
        <Panel className="flex flex-col items-center justify-center py-16">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 text-primary">
            <Building className="h-8 w-8" />
          </div>
          <h2 className="mt-4 text-lg font-medium text-foreground">
            Aucune SCI
          </h2>
          <p className="mt-2 max-w-md text-center text-sm text-muted-foreground">
            Commencez par créer votre première SCI pour gérer votre patrimoine immobilier.
          </p>
          <Button onClick={handleAdd} className="mt-6 gap-2">
            <Plus className="h-4 w-4" />
            Créer ma première SCI
          </Button>
        </Panel>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {scis.map((sci) => (
            <Panel key={sci.id} className="group relative overflow-hidden">
              {/* Header */}
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
                    <Building className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">{sci.nom}</h3>
                    <p className="text-xs text-muted-foreground">{sci.forme_juridique}</p>
                  </div>
                </div>
                <div className="flex gap-1 opacity-0 transition-opacity group-hover:opacity-100">
                  <Button
                    size="icon-sm"
                    variant="ghost"
                    onClick={() => handleEdit(sci)}
                    title="Modifier"
                  >
                    <Pencil className="h-4 w-4" />
                  </Button>
                  <Button
                    size="icon-sm"
                    variant="ghost"
                    onClick={() => handleDelete(sci)}
                    title="Supprimer"
                    className="text-destructive hover:text-destructive"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {/* Info */}
              <div className="mt-4 space-y-3">
                {sci.siret && (
                  <div className="flex items-center gap-2 text-sm">
                    <span className="font-medium text-muted-foreground">SIRET:</span>
                    <span className="font-mono text-xs">{sci.siret}</span>
                  </div>
                )}

                {sci.capital && (
                  <div className="flex items-center gap-2 text-sm">
                    <Euro className="h-4 w-4 text-muted-foreground" />
                    <span className="font-medium">Capital:</span>
                    <span className="font-mono">{formatCurrency(sci.capital)}</span>
                  </div>
                )}

                {sci.siege_social && (
                  <div className="flex items-start gap-2 text-sm">
                    <MapPin className="h-4 w-4 text-muted-foreground mt-0.5" />
                    <span className="text-muted-foreground line-clamp-2">{sci.siege_social}</span>
                  </div>
                )}

                {(sci.gerant_nom || sci.gerant_prenom) && (
                  <div className="flex items-center gap-2 text-sm">
                    <Users className="h-4 w-4 text-muted-foreground" />
                    <span className="font-medium">Gérant:</span>
                    <span>{sci.gerant_prenom} {sci.gerant_nom}</span>
                  </div>
                )}

                {sci.date_creation && (
                  <div className="text-xs text-muted-foreground">
                    Créée le {formatDate(sci.date_creation)}
                  </div>
                )}
              </div>

              {/* Documents section */}
              <div className="mt-4 border-t border-border pt-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Documents</span>
                    <span className="text-xs text-muted-foreground">
                      ({documents[sci.id]?.length || 0})
                    </span>
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleUploadDocument(sci)}
                    className="h-8 gap-1.5"
                  >
                    <UploadIcon className="h-3.5 w-3.5" />
                    <span className="text-xs">Ajouter</span>
                  </Button>
                </div>

                {documents[sci.id]?.length > 0 ? (
                  <div className="space-y-2">
                    {documents[sci.id].slice(0, 3).map((doc) => (
                      <div
                        key={doc.id}
                        className="flex items-center justify-between rounded-lg border border-border bg-secondary/20 p-2 text-xs"
                      >
                        <div className="flex items-center gap-2 flex-1 min-w-0">
                          <FileText className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                          <div className="min-w-0 flex-1">
                            <p className="truncate font-medium">{doc.nom_fichier}</p>
                            <p className="text-muted-foreground">
                              {DOCUMENT_TYPE_LABELS[doc.type_document]}
                            </p>
                          </div>
                        </div>
                        <div className="flex gap-1 shrink-0">
                          <Button
                            size="icon-sm"
                            variant="ghost"
                            onClick={() => window.open(doc.s3_url, '_blank')}
                            title="Télécharger"
                          >
                            <Download className="h-3 w-3" />
                          </Button>
                          <Button
                            size="icon-sm"
                            variant="ghost"
                            onClick={() => handleDeleteDocument(doc.id)}
                            title="Supprimer"
                            className="text-destructive hover:text-destructive"
                          >
                            <X className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    ))}
                    {documents[sci.id].length > 3 && (
                      <p className="text-xs text-center text-muted-foreground">
                        +{documents[sci.id].length - 3} document(s) supplémentaire(s)
                      </p>
                    )}
                  </div>
                ) : (
                  <p className="text-xs text-center text-muted-foreground py-4">
                    Aucun document
                  </p>
                )}
              </div>
            </Panel>
          ))}
        </div>
      )}

      <SCIFormDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        onSuccess={loadSCIs}
        sci={selectedSCI}
      />

      {selectedSCIForDocs && (
        <DocumentUploadDialog
          open={documentDialogOpen}
          onOpenChange={setDocumentDialogOpen}
          sciId={selectedSCIForDocs.id}
          onSuccess={loadSCIs}
        />
      )}
    </div>
  )
}
