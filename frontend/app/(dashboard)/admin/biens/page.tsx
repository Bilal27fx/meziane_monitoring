'use client'

import { useEffect, useState } from 'react'
import { Panel } from '@/components/ui/Panel'
import { Button } from '@/components/ui/button'
import { BienFormDialog } from '@/components/admin/BienFormDialog'
import { DocumentUploadDialog } from '@/components/admin/DocumentUploadDialog'
import { biensApi, type Bien, TYPE_BIEN_LABELS, STATUT_BIEN_LABELS, CLASSE_DPE_LABELS } from '@/lib/api/biens'
import { documentsApi, type Document, DOCUMENT_TYPE_LABELS } from '@/lib/api/documents'
import { Plus, Building2, Pencil, Trash2, MapPin, Home, Layers, Euro, FileText, Upload as UploadIcon, Download, X } from 'lucide-react'
import { toast } from 'sonner'
import { formatCurrency, formatDate } from '@/lib/utils/format'

export default function BiensPage() {
  const [biens, setBiens] = useState<Bien[]>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [documentDialogOpen, setDocumentDialogOpen] = useState(false)
  const [selectedBien, setSelectedBien] = useState<Bien | undefined>()
  const [selectedBienForDocs, setSelectedBienForDocs] = useState<Bien | undefined>()
  const [documents, setDocuments] = useState<Record<number, Document[]>>({})

  const loadBiens = async () => {
    try {
      setLoading(true)
      const data = await biensApi.getAll()
      setBiens(data)

      // Load documents for each bien
      const docsMap: Record<number, Document[]> = {}
      await Promise.all(
        data.map(async (bien) => {
          try {
            const docs = await documentsApi.getBySCI(bien.sci_id)
            // Filter documents for this specific bien
            docsMap[bien.id] = docs.filter(doc => doc.bien_id === bien.id)
          } catch (error) {
            docsMap[bien.id] = []
          }
        })
      )
      setDocuments(docsMap)
    } catch (error) {
      console.error('Error loading biens:', error)
      toast.error('Erreur lors du chargement des biens')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadBiens()
  }, [])

  const handleAdd = () => {
    setSelectedBien(undefined)
    setDialogOpen(true)
  }

  const handleEdit = (bien: Bien) => {
    setSelectedBien(bien)
    setDialogOpen(true)
  }

  const handleDelete = async (bien: Bien) => {
    if (!confirm(`Êtes-vous sûr de vouloir supprimer ce bien à "${bien.adresse}" ?`)) {
      return
    }

    try {
      await biensApi.delete(bien.id)
      toast.success('Bien supprimé avec succès')
      loadBiens()
    } catch (error: any) {
      console.error('Error deleting bien:', error)
      toast.error(error.response?.data?.detail || 'Erreur lors de la suppression')
    }
  }

  const handleUploadDocument = (bien: Bien) => {
    setSelectedBienForDocs(bien)
    setDocumentDialogOpen(true)
  }

  const handleDeleteDocument = async (documentId: number) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce document ?')) {
      return
    }

    try {
      await documentsApi.delete(documentId)
      toast.success('Document supprimé avec succès')
      loadBiens()
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
          <p className="text-sm text-muted-foreground">Chargement des biens...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Biens immobiliers</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Gérez votre portefeuille immobilier
          </p>
        </div>
        <Button onClick={handleAdd} className="gap-2">
          <Plus className="h-4 w-4" />
          Ajouter un bien
        </Button>
      </div>

      {biens.length === 0 ? (
        <Panel className="flex flex-col items-center justify-center py-16">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 text-primary">
            <Building2 className="h-8 w-8" />
          </div>
          <h2 className="mt-4 text-lg font-medium text-foreground">
            Aucun bien immobilier
          </h2>
          <p className="mt-2 max-w-md text-center text-sm text-muted-foreground">
            Commencez par ajouter votre premier bien immobilier pour construire votre patrimoine.
          </p>
          <Button onClick={handleAdd} className="mt-6 gap-2">
            <Plus className="h-4 w-4" />
            Créer mon premier bien
          </Button>
        </Panel>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {biens.map((bien) => (
            <Panel key={bien.id} className="group relative overflow-hidden">
              {/* Header */}
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
                    <Building2 className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">{TYPE_BIEN_LABELS[bien.type_bien]}</h3>
                    <p className="text-xs text-muted-foreground">{bien.ville}</p>
                  </div>
                </div>
                <div className="flex gap-1 opacity-0 transition-opacity group-hover:opacity-100">
                  <Button
                    size="icon-sm"
                    variant="ghost"
                    onClick={() => handleEdit(bien)}
                    title="Modifier"
                  >
                    <Pencil className="h-4 w-4" />
                  </Button>
                  <Button
                    size="icon-sm"
                    variant="ghost"
                    onClick={() => handleDelete(bien)}
                    title="Supprimer"
                    className="text-destructive hover:text-destructive"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {/* Statut badge */}
              <div className="mt-3">
                <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                  bien.statut === 'loue' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' :
                  bien.statut === 'vacant' ? 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400' :
                  bien.statut === 'travaux' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400' :
                  'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400'
                }`}>
                  {STATUT_BIEN_LABELS[bien.statut]}
                </span>
              </div>

              {/* Info */}
              <div className="mt-4 space-y-3">
                <div className="flex items-start gap-2 text-sm">
                  <MapPin className="h-4 w-4 text-muted-foreground mt-0.5 shrink-0" />
                  <span className="text-muted-foreground line-clamp-2">
                    {bien.adresse}
                    {bien.complement_adresse && `, ${bien.complement_adresse}`}
                    <br />
                    {bien.code_postal} {bien.ville}
                  </span>
                </div>

                {(bien.surface || bien.nb_pieces) && (
                  <div className="flex items-center gap-4 text-sm">
                    {bien.surface && (
                      <div className="flex items-center gap-1.5">
                        <Home className="h-4 w-4 text-muted-foreground" />
                        <span className="font-medium">{bien.surface} m²</span>
                      </div>
                    )}
                    {bien.nb_pieces && (
                      <div className="flex items-center gap-1.5">
                        <Layers className="h-4 w-4 text-muted-foreground" />
                        <span className="font-medium">{bien.nb_pieces} pièces</span>
                      </div>
                    )}
                  </div>
                )}

                {bien.etage !== undefined && bien.etage !== null && (
                  <div className="text-sm text-muted-foreground">
                    Étage {bien.etage}
                  </div>
                )}

                {(bien.prix_acquisition || bien.valeur_actuelle) && (
                  <div className="flex items-center gap-2 text-sm">
                    <Euro className="h-4 w-4 text-muted-foreground" />
                    <div className="flex flex-col">
                      {bien.prix_acquisition && (
                        <div>
                          <span className="text-muted-foreground">Acquisition: </span>
                          <span className="font-mono font-medium">{formatCurrency(bien.prix_acquisition)}</span>
                        </div>
                      )}
                      {bien.valeur_actuelle && (
                        <div>
                          <span className="text-muted-foreground">Valeur: </span>
                          <span className="font-mono font-medium">{formatCurrency(bien.valeur_actuelle)}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {bien.dpe_classe && (
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-muted-foreground">DPE:</span>
                    <span className={`inline-flex items-center justify-center h-6 w-6 rounded font-bold text-xs ${
                      bien.dpe_classe === 'A' ? 'bg-green-600 text-white' :
                      bien.dpe_classe === 'B' ? 'bg-green-500 text-white' :
                      bien.dpe_classe === 'C' ? 'bg-lime-500 text-white' :
                      bien.dpe_classe === 'D' ? 'bg-yellow-500 text-white' :
                      bien.dpe_classe === 'E' ? 'bg-orange-500 text-white' :
                      bien.dpe_classe === 'F' ? 'bg-red-500 text-white' :
                      bien.dpe_classe === 'G' ? 'bg-red-700 text-white' :
                      'bg-gray-400 text-white'
                    }`}>
                      {bien.dpe_classe}
                    </span>
                    {bien.dpe_date_validite && (
                      <span className="text-xs text-muted-foreground">
                        Valide jusqu'au {formatDate(bien.dpe_date_validite)}
                      </span>
                    )}
                  </div>
                )}

                {bien.date_acquisition && (
                  <div className="text-xs text-muted-foreground">
                    Acquis le {formatDate(bien.date_acquisition)}
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
                      ({documents[bien.id]?.length || 0})
                    </span>
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleUploadDocument(bien)}
                    className="h-8 gap-1.5"
                  >
                    <UploadIcon className="h-3.5 w-3.5" />
                    <span className="text-xs">Ajouter</span>
                  </Button>
                </div>

                {documents[bien.id]?.length > 0 ? (
                  <div className="space-y-2">
                    {documents[bien.id].slice(0, 3).map((doc) => (
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
                    {documents[bien.id].length > 3 && (
                      <p className="text-xs text-center text-muted-foreground">
                        +{documents[bien.id].length - 3} document(s) supplémentaire(s)
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

      <BienFormDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        onSuccess={loadBiens}
        bien={selectedBien}
      />

      {selectedBienForDocs && (
        <DocumentUploadDialog
          open={documentDialogOpen}
          onOpenChange={setDocumentDialogOpen}
          sciId={selectedBienForDocs.sci_id}
          bienId={selectedBienForDocs.id}
          onSuccess={loadBiens}
        />
      )}
    </div>
  )
}
