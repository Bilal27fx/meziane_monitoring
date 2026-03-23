// ─── Core Entities ───────────────────────────────────────────────────────────

export interface SCI {
  id: number
  nom: string
  siret?: string
  forme_juridique?: string
  capital_social?: number
  adresse_siege?: string
  date_creation?: string
  email?: string
  nb_biens?: number
  valeur_totale?: number
  cashflow_mensuel?: number
  created_at: string
  updated_at: string
}

export interface Bien {
  id: number
  sci_id: number
  sci?: SCI
  adresse: string
  complement?: string
  ville: string
  code_postal: string
  type: 'appartement' | 'maison' | 'bureau' | 'commerce' | 'terrain' | 'parking'
  surface?: number
  nb_pieces?: number
  etage?: number
  dpe?: 'A' | 'B' | 'C' | 'D' | 'E' | 'F' | 'G'
  validite_dpe?: string
  prix_acquisition?: number
  date_acquisition?: string
  valeur_actuelle?: number
  statut: 'loue' | 'vacant' | 'travaux' | 'vente'
  loyer_mensuel?: number
  tri_net?: number
  created_at: string
  updated_at: string
}

export interface Locataire {
  id: number
  prenom: string
  nom: string
  email: string
  telephone?: string
  date_naissance?: string
  profession?: string
  revenus_annuels?: number
  bien_id?: number
  bien?: Bien
  bail?: Bail
  statut_paiement?: 'a_jour' | 'retard' | 'impaye'
  jours_retard?: number
  created_at: string
  updated_at: string
}

export interface Bail {
  id: number
  locataire_id: number
  bien_id: number
  date_debut: string
  date_fin?: string
  loyer: number
  charges: number
  depot_garantie?: number
  type_revision?: 'IRL' | 'ILC' | 'fixe'
  created_at: string
  updated_at: string
}

export interface Transaction {
  id: number
  sci_id: number
  sci?: SCI
  bien_id?: number
  bien?: Bien
  libelle: string
  categorie: string
  montant: number
  date: string
  statut: 'valide' | 'en_attente' | 'rejete'
  type: 'revenu' | 'depense'
  created_at: string
  updated_at: string
}

export interface Quittance {
  id: number
  locataire_id: number
  mois: string
  montant: number
  statut: 'payee' | 'en_attente' | 'impayee'
  date_paiement?: string
  created_at: string
}

export interface Opportunite {
  id: number
  adresse: string
  ville: string
  prix: number
  surface?: number
  nb_pieces?: number
  dpe?: string
  tri_estime?: number
  score: number
  statut: 'nouveau' | 'vu' | 'analyse' | 'rejete' | 'favori'
  source?: string
  url?: string
  analyse_ia?: string
  risques?: string[]
  created_at: string
  updated_at: string
}

export interface User {
  id: number
  email: string
  prenom?: string
  nom?: string
  role: 'admin' | 'agent' | 'viewer'
  is_active: boolean
  created_at: string
  last_login?: string
}

// ─── Dashboard ───────────────────────────────────────────────────────────────

export interface DashboardKPIs {
  patrimoine_net: number
  patrimoine_net_change: number
  cashflow_mensuel: number
  cashflow_mensuel_change: number
  taux_occupation: number
  taux_occupation_change: number
  nb_biens: number
  nb_biens_change: number
}

export interface DashboardFull {
  kpis: DashboardKPIs
  cashflow_history: { date: string; value: number }[]
  patrimoine_history: { date: string; value: number }[]
  top_biens: TopBien[]
  recent_transactions: Transaction[]
  sci_overview: SCIOverviewItem[]
  opportunites_count: number
  locataires_actifs: number
}

export interface TopBien {
  id: number
  adresse: string
  sci_nom: string
  valeur: number
  tri_net: number
  rank: number
}

export interface SCIOverviewItem {
  id: number
  nom: string
  cashflow_mensuel: number
  nb_biens: number
  valeur_totale: number
}

// ─── Agent / Task ────────────────────────────────────────────────────────────

export interface CeleryTask {
  id: string
  name: string
  statut: 'ok' | 'warning' | 'error' | 'running' | 'pending'
  derniere_exec?: string
  prochaine_exec?: string
  tasks_24h?: number
  succes?: number
  erreurs?: number
  en_attente?: number
}

export interface AgentConfig {
  villes_cibles: string[]
  budget_max: number
  tri_minimum: number
  sources: string[]
}

// ─── API Response Shapes ─────────────────────────────────────────────────────

export interface ApiResponse<T> {
  data: T
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  pages: number
}

export interface ApiError {
  detail: string
  status_code?: number
}

// ─── Auth ─────────────────────────────────────────────────────────────────────

export interface AuthTokens {
  access_token: string
  token_type: string
}

export interface LoginCredentials {
  username: string
  password: string
}

// ─── Filter Params ────────────────────────────────────────────────────────────

export interface SCIParams {
  page?: number
  per_page?: number
  search?: string
}

export interface BienParams {
  page?: number
  per_page?: number
  sci_id?: number
  statut?: string
  search?: string
}

export interface LocataireParams {
  page?: number
  per_page?: number
  bien_id?: number
  statut_paiement?: string
  search?: string
}

export interface TransactionParams {
  page?: number
  per_page?: number
  sci_id?: number
  categorie?: string
  statut?: string
  type?: string
  date_debut?: string
  date_fin?: string
}

export interface OpportuniteParams {
  page?: number
  per_page?: number
  statut?: string
  score_min?: number
}

// ─── Form Data ────────────────────────────────────────────────────────────────

export interface SCIFormData {
  nom: string
  siret?: string
  forme_juridique?: string
  capital_social?: number
  adresse_siege?: string
  date_creation?: string
  email?: string
}

export interface BienFormData {
  sci_id: number
  adresse: string
  complement?: string
  ville: string
  code_postal: string
  type: string
  surface?: number
  nb_pieces?: number
  etage?: number
  dpe?: string
  validite_dpe?: string
  prix_acquisition?: number
  date_acquisition?: string
  valeur_actuelle?: number
  statut: string
}

export interface LocataireFormData {
  prenom: string
  nom: string
  email: string
  telephone?: string
  date_naissance?: string
  profession?: string
  revenus_annuels?: number
  bien_id?: number
  date_debut?: string
  date_fin?: string
  loyer?: number
  charges?: number
  depot_garantie?: number
  type_revision?: string
}
