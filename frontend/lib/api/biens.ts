import { apiClient } from './client'

export enum TypeBien {
  APPARTEMENT = 'appartement',
  STUDIO = 'studio',
  MAISON = 'maison',
  LOCAL_COMMERCIAL = 'local_commercial',
  IMMEUBLE = 'immeuble',
  PARKING = 'parking',
  AUTRE = 'autre',
}

export enum StatutBien {
  LOUE = 'loue',
  VACANT = 'vacant',
  TRAVAUX = 'travaux',
  VENTE = 'vente',
}

export enum ClasseDPE {
  A = 'A',
  B = 'B',
  C = 'C',
  D = 'D',
  E = 'E',
  F = 'F',
  G = 'G',
  NON_RENSEIGNE = 'non_renseigne',
}

export const TYPE_BIEN_LABELS: Record<TypeBien, string> = {
  [TypeBien.APPARTEMENT]: 'Appartement',
  [TypeBien.STUDIO]: 'Studio',
  [TypeBien.MAISON]: 'Maison',
  [TypeBien.LOCAL_COMMERCIAL]: 'Local commercial',
  [TypeBien.IMMEUBLE]: 'Immeuble',
  [TypeBien.PARKING]: 'Parking',
  [TypeBien.AUTRE]: 'Autre',
}

export const STATUT_BIEN_LABELS: Record<StatutBien, string> = {
  [StatutBien.LOUE]: 'Loué',
  [StatutBien.VACANT]: 'Vacant',
  [StatutBien.TRAVAUX]: 'En travaux',
  [StatutBien.VENTE]: 'En vente',
}

export const CLASSE_DPE_LABELS: Record<ClasseDPE, string> = {
  [ClasseDPE.A]: 'A',
  [ClasseDPE.B]: 'B',
  [ClasseDPE.C]: 'C',
  [ClasseDPE.D]: 'D',
  [ClasseDPE.E]: 'E',
  [ClasseDPE.F]: 'F',
  [ClasseDPE.G]: 'G',
  [ClasseDPE.NON_RENSEIGNE]: 'Non renseigné',
}

export interface Bien {
  id: number
  sci_id: number
  adresse: string
  ville: string
  code_postal: string
  complement_adresse?: string
  type_bien: TypeBien
  surface?: number
  nb_pieces?: number
  etage?: number
  date_acquisition?: string
  prix_acquisition?: number
  valeur_actuelle?: number
  dpe_classe?: ClasseDPE
  dpe_date_validite?: string
  statut: StatutBien
}

export interface BienCreate {
  sci_id: number
  adresse: string
  ville: string
  code_postal: string
  complement_adresse?: string
  type_bien: TypeBien
  surface?: number
  nb_pieces?: number
  etage?: number
  date_acquisition?: string
  prix_acquisition?: number
  valeur_actuelle?: number
  dpe_classe?: ClasseDPE
  dpe_date_validite?: string
  statut?: StatutBien
}

export interface BienUpdate {
  sci_id?: number
  adresse?: string
  ville?: string
  code_postal?: string
  complement_adresse?: string
  type_bien?: TypeBien
  surface?: number
  nb_pieces?: number
  etage?: number
  date_acquisition?: string
  prix_acquisition?: number
  valeur_actuelle?: number
  dpe_classe?: ClasseDPE
  dpe_date_validite?: string
  statut?: StatutBien
}

export const biensApi = {
  async getAll(sciId?: number): Promise<Bien[]> {
    const params = sciId ? { sci_id: sciId } : {}
    const response = await apiClient.get('/api/biens/', { params })
    return response.data
  },

  async getById(id: number): Promise<Bien> {
    const response = await apiClient.get(`/api/biens/${id}`)
    return response.data
  },

  async create(data: BienCreate): Promise<Bien> {
    const response = await apiClient.post('/api/biens/', data)
    return response.data
  },

  async update(id: number, data: BienUpdate): Promise<Bien> {
    const response = await apiClient.put(`/api/biens/${id}`, data)
    return response.data
  },

  async delete(id: number): Promise<void> {
    await apiClient.delete(`/api/biens/${id}`)
  },
}
