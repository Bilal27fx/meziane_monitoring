import { apiClient } from './client'

export enum TypeDocument {
  // SCI / Bien
  FACTURE = 'facture',
  RELEVE_BANCAIRE = 'releve_bancaire',
  TAXE_FONCIERE = 'taxe_fonciere',
  BAIL = 'bail',
  DIAGNOSTIC_DPE = 'diagnostic_dpe',
  DIAGNOSTIC_AMIANTE = 'diagnostic_amiante',
  STATUTS_SCI = 'statuts_sci',
  KBIS = 'kbis',

  // Locataire
  PIECE_IDENTITE = 'piece_identite',
  JUSTIFICATIF_DOMICILE = 'justificatif_domicile',
  CONTRAT_TRAVAIL = 'contrat_travail',
  FICHE_PAIE = 'fiche_paie',
  AVIS_IMPOSITION = 'avis_imposition',
  RIB = 'rib',
  ASSURANCE_HABITATION = 'assurance_habitation',
  ACTE_CAUTION_SOLIDAIRE = 'acte_caution_solidaire',
  QUITTANCE_LOYER_PRECEDENTE = 'quittance_loyer_precedente',

  AUTRE = 'autre',
}

export const SCI_DOCUMENT_TYPES = [
  TypeDocument.STATUTS_SCI,
  TypeDocument.KBIS,
  TypeDocument.RELEVE_BANCAIRE,
  TypeDocument.FACTURE,
  TypeDocument.TAXE_FONCIERE,
  TypeDocument.AUTRE,
]

export const BIEN_DOCUMENT_TYPES = [
  TypeDocument.BAIL,
  TypeDocument.DIAGNOSTIC_DPE,
  TypeDocument.DIAGNOSTIC_AMIANTE,
  TypeDocument.FACTURE,
  TypeDocument.TAXE_FONCIERE,
  TypeDocument.RELEVE_BANCAIRE,
  TypeDocument.AUTRE,
]

export const LOCATAIRE_DOCUMENT_TYPES = [
  TypeDocument.PIECE_IDENTITE,
  TypeDocument.JUSTIFICATIF_DOMICILE,
  TypeDocument.CONTRAT_TRAVAIL,
  TypeDocument.FICHE_PAIE,
  TypeDocument.AVIS_IMPOSITION,
  TypeDocument.RIB,
  TypeDocument.ASSURANCE_HABITATION,
  TypeDocument.ACTE_CAUTION_SOLIDAIRE,
  TypeDocument.QUITTANCE_LOYER_PRECEDENTE,
  TypeDocument.AUTRE,
]

export const DOCUMENT_TYPE_LABELS: Record<TypeDocument, string> = {
  [TypeDocument.FACTURE]: 'Facture',
  [TypeDocument.RELEVE_BANCAIRE]: 'Relevé bancaire',
  [TypeDocument.TAXE_FONCIERE]: 'Taxe foncière',
  [TypeDocument.BAIL]: 'Bail',
  [TypeDocument.DIAGNOSTIC_DPE]: 'Diagnostic DPE',
  [TypeDocument.DIAGNOSTIC_AMIANTE]: 'Diagnostic Amiante',
  [TypeDocument.STATUTS_SCI]: 'Statuts SCI',
  [TypeDocument.KBIS]: 'KBIS',
  [TypeDocument.PIECE_IDENTITE]: 'Pièce d\'identité',
  [TypeDocument.JUSTIFICATIF_DOMICILE]: 'Justificatif de domicile',
  [TypeDocument.CONTRAT_TRAVAIL]: 'Contrat de travail',
  [TypeDocument.FICHE_PAIE]: 'Fiche de paie',
  [TypeDocument.AVIS_IMPOSITION]: 'Avis d\'imposition',
  [TypeDocument.RIB]: 'RIB',
  [TypeDocument.ASSURANCE_HABITATION]: 'Assurance habitation',
  [TypeDocument.ACTE_CAUTION_SOLIDAIRE]: 'Acte de caution solidaire',
  [TypeDocument.QUITTANCE_LOYER_PRECEDENTE]: 'Quittance de loyer précédente',
  [TypeDocument.AUTRE]: 'Autre',
}

export interface Document {
  id: number
  sci_id: number
  bien_id?: number
  locataire_id?: number
  type_document: TypeDocument
  s3_url: string
  nom_fichier: string
  date_document?: string
  uploaded_at: string
  metadata?: any
}

export interface DocumentUpload {
  sci_id: number
  type_document: TypeDocument
  file: File
  bien_id?: number
  locataire_id?: number
  date_document?: string
  metadata_json?: string
}

export const documentsApi = {
  async getBySCI(sciId: number): Promise<Document[]> {
    const response = await apiClient.get(`/api/documents/sci/${sciId}`)
    return response.data
  },

  async getByLocataire(locataireId: number): Promise<Document[]> {
    const response = await apiClient.get(`/api/documents/locataire/${locataireId}`)
    return response.data
  },

  async upload(data: DocumentUpload): Promise<Document> {
    const formData = new FormData()
    formData.append('sci_id', data.sci_id.toString())
    formData.append('type_document', data.type_document)
    formData.append('file', data.file)

    if (data.bien_id) {
      formData.append('bien_id', data.bien_id.toString())
    }
    if (data.locataire_id) {
      formData.append('locataire_id', data.locataire_id.toString())
    }
    if (data.date_document) {
      formData.append('date_document', data.date_document)
    }
    if (data.metadata_json) {
      formData.append('metadata_json', data.metadata_json)
    }

    const response = await apiClient.post('/api/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  async delete(documentId: number): Promise<void> {
    await apiClient.delete(`/api/documents/${documentId}`)
  },

  getDownloadUrl(document: Document): string {
    return document.s3_url
  },
}
