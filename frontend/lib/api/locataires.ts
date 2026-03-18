import { apiClient } from './client'

export interface Locataire {
  id: number
  nom: string
  prenom: string
  email?: string
  telephone?: string
  date_naissance?: string
  profession?: string
  revenus_annuels?: number
}

export interface LocataireCreate {
  nom: string
  prenom: string
  email: string
  telephone: string
  date_naissance: string
  profession: string
  revenus_annuels: number
}

export interface LocataireUpdate {
  nom?: string
  prenom?: string
  email?: string
  telephone?: string
  date_naissance?: string
  profession?: string
  revenus_annuels?: number
}

export const locatairesApi = {
  async getAll(): Promise<Locataire[]> {
    const response = await apiClient.get('/api/locataires/')
    return response.data
  },

  async getById(id: number): Promise<Locataire> {
    const response = await apiClient.get(`/api/locataires/${id}`)
    return response.data
  },

  async create(data: LocataireCreate): Promise<Locataire> {
    const response = await apiClient.post('/api/locataires/', data)
    return response.data
  },

  async update(id: number, data: LocataireUpdate): Promise<Locataire> {
    const response = await apiClient.put(`/api/locataires/${id}`, data)
    return response.data
  },

  async delete(id: number): Promise<void> {
    await apiClient.delete(`/api/locataires/${id}`)
  },
}
