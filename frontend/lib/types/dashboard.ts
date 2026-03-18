export interface KpiData {
  label: string
  value: number
  change: number
  changeLabel: string
  prefix?: string
  suffix?: string
}

export interface CashflowPoint {
  date: string
  entrees: number
  sorties: number
  net: number
}

export interface PatrimoinePoint {
  date: string
  valeur: number
}

export interface Transaction {
  id: string
  date: string
  type: 'LOYER' | 'CHARGE' | 'TRAVAUX' | 'IMPOT' | 'AUTRE'
  description: string
  montant: number
  bien: string
}

export interface Bien {
  id: string
  nom: string
  ville: string
  valeur: number
  rendement: number
  occupation: number
}

export interface SCI {
  id: string
  nom: string
  nbBiens: number
  valeur: number
  cashflow: number
}

export interface Locataire {
  id: string
  nom: string
  bien: string
  loyer: number
  finBail: string
  statut: 'OK' | 'RETARD' | 'IMPAYE'
}

export interface Opportunite {
  id: string
  titre: string
  type: string
  score: number
  description: string
}

export interface SimulationResult {
  prix: number
  loyer: number
  rendement: number
  cashflow: number
  roi: number
}

export interface DashboardData {
  kpis: {
    patrimoineNet: KpiData
    cashflowToday: KpiData
    alertesIA: KpiData
    performanceYTD: KpiData
  }
  cashflow30j: CashflowPoint[]
  patrimoine12m: PatrimoinePoint[]
  transactions: Transaction[]
  topBiens: Bien[]
  scis: SCI[]
  locataires: Locataire[]
  opportunites: Opportunite[]
}
