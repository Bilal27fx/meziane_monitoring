import { apiClient } from './client'

export interface SCI {
  id: number
  nom: string
  forme_juridique: string
  siret?: string
  date_creation?: string
  capital?: number
  siege_social?: string
  gerant_nom?: string
  gerant_prenom?: string
}

export interface SCICreate {
  nom: string
  forme_juridique?: string
  siret?: string
  date_creation?: string
  capital?: number
  siege_social?: string
  gerant_nom?: string
  gerant_prenom?: string
}

export interface SCIUpdate {
  nom?: string
  forme_juridique?: string
  siret?: string
  date_creation?: string
  capital?: number
  siege_social?: string
  gerant_nom?: string
  gerant_prenom?: string
}

export const sciApi = {
  async getAll(): Promise<SCI[]> {
    const response = await apiClient.get('/api/sci/')
    return response.data
  },

  async getById(id: number): Promise<SCI> {
    const response = await apiClient.get(`/api/sci/${id}`)
    return response.data
  },

  async create(data: SCICreate): Promise<SCI> {
    const response = await apiClient.post('/api/sci/', data)
    return response.data
  },

  async update(id: number, data: SCIUpdate): Promise<SCI> {
    const response = await apiClient.put(`/api/sci/${id}`, data)
    return response.data
  },

  async delete(id: number): Promise<void> {
    await apiClient.delete(`/api/sci/${id}`)
  },

  async getPatrimoineStats(): Promise<any> {
    const response = await apiClient.get('/api/sci/stats/patrimoine')
    return response.data
  },
}
