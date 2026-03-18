import { apiClient } from './client'

export interface DashboardKPI {
  patrimoine_net: number
  cashflow_today: number
  nb_alertes: number
  performance_ytd: number
  taux_occupation: number
  nb_locataires_actifs: number
}

export interface CashflowDataPoint {
  date: string
  revenus: number
  depenses: number
  net: number
}

export interface PatrimoineDataPoint {
  mois: string
  valeur: number
}

export interface Transaction {
  id: number
  date: string
  type: string
  description: string
  montant: number
  bien_adresse?: string
  sci_nom?: string
}

export interface TopBien {
  id: number
  adresse: string
  sci_nom: string
  rentabilite_nette: number
  loyer_mensuel: number
  valeur_actuelle: number
}

export interface SCIOverview {
  id: number
  nom: string
  nb_biens: number
  valeur_totale: number
  cashflow_mensuel: number
  revenus_annuels: number
  depenses_annuelles: number
}

export interface LocataireOverview {
  id: number
  nom: string
  prenom: string
  bien_adresse: string
  loyer_mensuel: number
  statut_paiement: string
  date_fin_bail?: string
}

export interface OpportuniteOverview {
  id: number
  type: string
  titre: string
  description: string
  score: number
  montant_estime?: number
  sci_id?: number
  bien_id?: number
  date_detection: string
}

export interface FullDashboardData {
  kpi: DashboardKPI
  cashflow_30j: CashflowDataPoint[]
  patrimoine_12m: PatrimoineDataPoint[]
  transactions: Transaction[]
  top_biens: TopBien[]
  scis: SCIOverview[]
  locataires: LocataireOverview[]
  opportunites: OpportuniteOverview[]
}

export const dashboardApi = {
  // Get full dashboard data in one call (optimized)
  async getFullDashboard(): Promise<FullDashboardData> {
    const response = await apiClient.get('/api/dashboard/full')
    return response.data
  },

  // Individual endpoint calls (if needed)
  async getKPI(): Promise<DashboardKPI> {
    const response = await apiClient.get('/api/dashboard/kpi')
    return response.data
  },

  async getCashflow(): Promise<CashflowDataPoint[]> {
    const response = await apiClient.get('/api/dashboard/cashflow')
    return response.data.data
  },

  async getPatrimoine(): Promise<PatrimoineDataPoint[]> {
    const response = await apiClient.get('/api/dashboard/patrimoine')
    return response.data.data
  },

  async getTransactions(limit: number = 10): Promise<Transaction[]> {
    const response = await apiClient.get(`/api/dashboard/transactions?limit=${limit}`)
    return response.data.data
  },

  async getTopBiens(limit: number = 5): Promise<TopBien[]> {
    const response = await apiClient.get(`/api/dashboard/biens/top5?limit=${limit}`)
    return response.data.data
  },

  async getSCIOverview(): Promise<SCIOverview[]> {
    const response = await apiClient.get('/api/dashboard/sci/overview')
    return response.data.data
  },

  async getLocataires(): Promise<LocataireOverview[]> {
    const response = await apiClient.get('/api/dashboard/locataires')
    return response.data.data
  },

  async getOpportunites(limit: number = 10): Promise<OpportuniteOverview[]> {
    const response = await apiClient.get(`/api/dashboard/opportunites?limit=${limit}`)
    return response.data.data
  },
}
