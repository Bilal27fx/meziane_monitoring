'use client'

import { useEffect, useState } from 'react'
import { Panel } from '@/components/ui/Panel'
import { Button } from '@/components/ui/button'
import { LocataireFormDialog } from '@/components/admin/LocataireFormDialog'
import { DocumentUploadDialog } from '@/components/admin/DocumentUploadDialog'
import { locatairesApi, type Locataire } from '@/lib/api/locataires'
import { documentsApi, type Document, DOCUMENT_TYPE_LABELS } from '@/lib/api/documents'
import { Plus, Users, Pencil, Trash2, Mail, Phone, Briefcase, Euro, Calendar, FileText, Upload as UploadIcon, Download, X } from 'lucide-react'
import { toast } from 'sonner'
import { formatCurrency, formatDate } from '@/lib/utils/format'

export default function LocatairesPage() {
  const [locataires, setLocataires] = useState<Locataire[]>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [documentDialogOpen, setDocumentDialogOpen] = useState(false)
  const [selectedLocataire, setSelectedLocataire] = useState<Locataire | undefined>()
  const [selectedLocataireForDocs, setSelectedLocataireForDocs] = useState<Locataire | undefined>()
  const [documents, setDocuments] = useState<Record<number, Document[]>>({})

  const loadLocataires = async () => {
    try {
      setLoading(true)
      const data = await locatairesApi.getAll()
      setLocataires(data)

      // Load documents for each locataire
      const docsMap: Record<number, Document[]> = {}
      await Promise.all(
        data.map(async (locataire) => {
          try {
            const docs = await documentsApi.getByLocataire(locataire.id)
            docsMap[locataire.id] = docs
          } catch (error) {
            docsMap[locataire.id] = []
          }
        })
      )
      setDocuments(docsMap)
    } catch (error) {
      console.error('Error loading locataires:', error)
      toast.error('Erreur lors du chargement des locataires')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadLocataires()
  }, [])

  const handleAdd = () => {
    setSelectedLocataire(undefined)
    setDialogOpen(true)
  }

  const handleEdit = (locataire: Locataire) => {
    setSelectedLocataire(locataire)
    setDialogOpen(true)
  }

  const handleDelete = async (locataire: Locataire) => {
    if (!confirm(`Êtes-vous sûr de vouloir supprimer le locataire "${locataire.prenom} ${locataire.nom}" ?`)) {
      return
    }

    try {
      await locatairesApi.delete(locataire.id)
      toast.success('Locataire supprimé avec succès')
      loadLocataires()
    } catch (error: any) {
      console.error('Error deleting locataire:', error)
      toast.error(error.response?.data?.detail || 'Erreur lors de la suppression')
    }
  }

  const handleUploadDocument = (locataire: Locataire) => {
    setSelectedLocataireForDocs(locataire)
    setDocumentDialogOpen(true)
  }

  const handleDeleteDocument = async (documentId: number) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce document ?')) {
      return
    }

    try {
      await documentsApi.delete(documentId)
      toast.success('Document supprimé avec succès')
      loadLocataires()
    } catch (error: any) {
      console.error('Error deleting document:', error)
      toast.error(error.response?.data?.detail || 'Erreur lors de la suppression')
    }
  }

  const calculateAge = (dateNaissance: string) => {
    const birth = new Date(dateNaissance)
    const today = new Date()
    let age = today.getFullYear() - birth.getFullYear()
    const monthDiff = today.getMonth() - birth.getMonth()
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--
    }
    return age
  }

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="text-center">
          <div className="mb-4 h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent mx-auto"></div>
          <p className="text-sm text-muted-foreground">Chargement des locataires...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Locataires</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Gérez vos locataires et leurs informations
          </p>
        </div>
        <Button onClick={handleAdd} className="gap-2">
          <Plus className="h-4 w-4" />
          Ajouter un locataire
        </Button>
      </div>

      {locataires.length === 0 ? (
        <Panel className="flex flex-col items-center justify-center py-16">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 text-primary">
            <Users className="h-8 w-8" />
          </div>
          <h2 className="mt-4 text-lg font-medium text-foreground">
            Aucun locataire
          </h2>
          <p className="mt-2 max-w-md text-center text-sm text-muted-foreground">
            Commencez par ajouter votre premier locataire pour gérer vos locations.
          </p>
          <Button onClick={handleAdd} className="mt-6 gap-2">
            <Plus className="h-4 w-4" />
            Créer mon premier locataire
          </Button>
        </Panel>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {locataires.map((locataire) => (
            <Panel key={locataire.id} className="group relative overflow-hidden">
              {/* Header */}
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
                    <Users className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">
                      {locataire.prenom} {locataire.nom}
                    </h3>
                    {locataire.date_naissance && (
                      <p className="text-xs text-muted-foreground">
                        {calculateAge(locataire.date_naissance)} ans
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex gap-1 opacity-0 transition-opacity group-hover:opacity-100">
                  <Button
                    size="icon-sm"
                    variant="ghost"
                    onClick={() => handleEdit(locataire)}
                    title="Modifier"
                  >
                    <Pencil className="h-4 w-4" />
                  </Button>
                  <Button
                    size="icon-sm"
                    variant="ghost"
                    onClick={() => handleDelete(locataire)}
                    title="Supprimer"
                    className="text-destructive hover:text-destructive"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {/* Info */}
              <div className="mt-4 space-y-3">
                {locataire.email && (
                  <div className="flex items-center gap-2 text-sm">
                    <Mail className="h-4 w-4 text-muted-foreground shrink-0" />
                    <a href={`mailto:${locataire.email}`} className="text-primary hover:underline truncate">
                      {locataire.email}
                    </a>
                  </div>
                )}

                {locataire.telephone && (
                  <div className="flex items-center gap-2 text-sm">
                    <Phone className="h-4 w-4 text-muted-foreground" />
                    <a href={`tel:${locataire.telephone}`} className="text-muted-foreground hover:text-foreground">
                      {locataire.telephone}
                    </a>
                  </div>
                )}

                {locataire.profession && (
                  <div className="flex items-center gap-2 text-sm">
                    <Briefcase className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">{locataire.profession}</span>
                  </div>
                )}

                {locataire.revenus_annuels && (
                  <div className="flex items-center gap-2 text-sm">
                    <Euro className="h-4 w-4 text-muted-foreground" />
                    <span className="font-medium">Revenus:</span>
                    <span className="font-mono">{formatCurrency(locataire.revenus_annuels)}/an</span>
                  </div>
                )}

                {locataire.date_naissance && (
                  <div className="flex items-center gap-2 text-sm">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <span className="text-xs text-muted-foreground">
                      Né(e) le {formatDate(locataire.date_naissance)}
                    </span>
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
                      ({documents[locataire.id]?.length || 0})
                    </span>
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleUploadDocument(locataire)}
                    className="h-8 gap-1.5"
                  >
                    <UploadIcon className="h-3.5 w-3.5" />
                    <span className="text-xs">Ajouter</span>
                  </Button>
                </div>

                {documents[locataire.id]?.length > 0 ? (
                  <div className="space-y-2">
                    {documents[locataire.id].slice(0, 3).map((doc) => (
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
                    {documents[locataire.id].length > 3 && (
                      <p className="text-xs text-center text-muted-foreground">
                        +{documents[locataire.id].length - 3} document(s) supplémentaire(s)
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

      <LocataireFormDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        onSuccess={loadLocataires}
        locataire={selectedLocataire}
      />

      {selectedLocataireForDocs && (
        <DocumentUploadDialog
          open={documentDialogOpen}
          onOpenChange={setDocumentDialogOpen}
          sciId={0}
          locataireId={selectedLocataireForDocs.id}
          onSuccess={loadLocataires}
        />
      )}
    </div>
  )
}
