// ─── Core Entities ───────────────────────────────────────────────────────────

export interface SCI {
  id: number
  nom: string
  siret?: string
  forme_juridique?: string
  capital?: number
  siege_social?: string
  gerant_nom?: string
  gerant_prenom?: string
  date_creation?: string
  nb_biens?: number
  valeur_totale?: number
  cashflow_mensuel?: number
}

export interface Bien {
  id: number
  sci_id: number
  sci_nom?: string
  adresse: string
  complement_adresse?: string
  ville: string
  code_postal: string
  type_bien: 'appartement' | 'studio' | 'maison' | 'local_commercial' | 'immeuble' | 'parking' | 'autre'
  surface?: number
  nb_pieces?: number
  etage?: number
  dpe_classe?: 'A' | 'B' | 'C' | 'D' | 'E' | 'F' | 'G' | 'non_renseigne'
  dpe_date_validite?: string
  prix_acquisition?: number
  date_acquisition?: string
  valeur_actuelle?: number
  statut: 'loue' | 'vacant' | 'travaux' | 'vente'
  loyer_mensuel?: number
  tri_net?: number
  statut_paiement?: 'a_jour' | 'retard' | 'impaye'
  jours_retard?: number
}

export interface BailInfo {
  id: number
  bien_id: number
  bien_adresse?: string
  loyer_mensuel: number
  charges_mensuelles: number
  depot_garantie?: number
  date_debut: string
  date_fin?: string
  statut: string
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
  bail?: BailInfo
  statut_paiement?: 'a_jour' | 'retard' | 'impaye'
  jours_retard?: number
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

export interface LocatairePaiement {
  id: number
  locataire_id: number
  bail_id: number
  quittance_id?: number
  date_paiement: string
  montant: number
  mode_paiement: 'virement' | 'prelevement' | 'carte' | 'cheque' | 'especes' | 'autre'
  reference?: string
  note?: string
  created_at: string
}

export interface LocatairePaiementMonthStatus {
  key: string
  label: string
  quittance_id?: number
  statut: 'payee' | 'partielle' | 'impayee' | 'en_attente' | 'a_generer'
  montant_du: number
  montant_paye: number
  solde: number
  date_paiement?: string
}

export interface LocatairePaiementYearSummary {
  annee: number
  total_du: number
  total_paye: number
  reste_a_payer: number
  mensualites_total: number
  mensualites_reglees: number
  mensualites_en_retard: number
}

export interface LocatairePaiementOverview {
  locataire_id: number
  bail_id?: number
  date_debut_bail?: string
  date_fin_bail?: string
  montant_mensuel: number
  total_du: number
  total_paye: number
  reste_a_payer: number
  mensualites_total: number
  mensualites_reglees: number
  mensualites_en_retard: number
  paiements: LocatairePaiement[]
  derniers_mois: LocatairePaiementMonthStatus[]
  historique_mensuel: LocatairePaiementMonthStatus[]
  resume_annuel: LocatairePaiementYearSummary[]
}

export type TypeDocument =
  | 'facture'
  | 'releve_bancaire'
  | 'taxe_fonciere'
  | 'bail'
  | 'diagnostic_dpe'
  | 'diagnostic_amiante'
  | 'statuts_sci'
  | 'kbis'
  | 'piece_identite'
  | 'justificatif_domicile'
  | 'contrat_travail'
  | 'fiche_paie'
  | 'avis_imposition'
  | 'rib'
  | 'assurance_habitation'
  | 'acte_caution_solidaire'
  | 'quittance_loyer_precedente'
  | 'autre'

export interface Document {
  id: number
  sci_id: number
  bien_id?: number
  locataire_id?: number
  folder_id?: number
  type_document: TypeDocument
  nom_fichier: string
  s3_url?: string
  date_document?: string
  uploaded_at: string
}

export interface DocumentFolder {
  id: number
  sci_id: number
  bien_id?: number
  locataire_id?: number
  parent_id?: number
  nom: string
  created_at: string
}

export interface DocumentLibrary {
  current_folder?: DocumentFolder | null
  folders: DocumentFolder[]
  documents: Document[]
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
  cashflow_today: number
  nb_alertes: number
  performance_ytd: number
  taux_occupation: number
  nb_locataires_actifs: number
}

export interface DashboardTransaction {
  id: number
  date: string
  montant: number
  libelle: string
  categorie?: string
  sci_nom?: string
  bien_adresse?: string
  statut_validation: string
}

export interface DashboardFull {
  kpi: DashboardKPIs
  cashflow_30days: { date: string; revenus: number; depenses: number; net: number }[]
  patrimoine_12months: { date: string; valeur: number }[]
  top_biens: TopBien[]
  recent_transactions: DashboardTransaction[]
  sci_overview: SCIOverviewItem[]
  locataires: LocataireOverview[]
  opportunites: OpportuniteOverview[]
}

export interface TopBien {
  id: number
  adresse: string
  ville: string
  type_bien: string
  valeur_actuelle: number
  rentabilite_brute: number
  rentabilite_nette: number
  cashflow_annuel: number
}

export interface SCIOverviewItem {
  id: number
  nom: string
  siret?: string
  nb_biens: number
  valeur_patrimoniale: number
  cashflow_annuel: number
  revenus_annuels: number
  depenses_annuelles: number
}

export interface LocataireOverview {
  id: number
  nom: string
  prenom: string
  email?: string
  telephone?: string
  bien_adresse?: string
  loyer_mensuel: number
  statut_paiement: string
  nb_impayes: number
  date_debut_bail: string
}

export interface OpportuniteOverview {
  id: number
  titre?: string
  ville: string
  prix: number
  surface?: number
  prix_m2?: number
  nb_pieces?: number
  score_global?: number
  rentabilite_brute?: number
  rentabilite_nette?: number
  source: string
  url_annonce: string
  date_detection: string
  statut: string
}

export interface ServicesHealth {
  api: 'online' | 'offline'
  database: 'online' | 'offline'
  celery: 'online' | 'offline'
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

export interface AuctionAgentRun {
  id: number
  agent_definition_id: number
  parameter_set_id?: number | null
  trigger_type: 'manual' | 'scheduled' | 'backfill'
  status: 'pending' | 'running' | 'success' | 'failed' | 'cancelled'
  parameter_snapshot: Record<string, unknown>
  prompt_snapshot?: Record<string, unknown> | null
  code_version?: string | null
  started_at: string
  finished_at?: string | null
  created_at: string
}

export interface AuctionAgentRunEvent {
  id: number
  run_id: number
  level: 'debug' | 'info' | 'warning' | 'error'
  step?: string | null
  event_type: string
  message: string
  payload?: Record<string, unknown> | null
  created_at: string
}

export interface AuctionListing {
  id: number
  source_id: number
  session_id: number
  external_id?: string | null
  source_url: string
  reference_annonce?: string | null
  title: string
  listing_type?: string | null
  reserve_price?: number | null
  city?: string | null
  postal_code?: string | null
  address?: string | null
  surface_m2?: number | null
  nb_pieces?: number | null
  nb_chambres?: number | null
  etage?: number | null
  type_etage?: string | null
  ascenseur?: boolean | null
  balcon?: boolean | null
  terrasse?: boolean | null
  cave?: boolean | null
  parking?: boolean | null
  box?: boolean | null
  jardin?: boolean | null
  property_details?: Record<string, unknown> | null
  occupancy_status?: string | null
  visit_dates?: string[] | null
  auction_date?: string | null
  status: 'discovered' | 'normalized' | 'enriched' | 'shortlisted' | 'rejected'
  published_at?: string | null
  last_seen_at: string
  created_at: string
  updated_at: string
  // Scoring LLM
  score_global?: number | null
  score_localisation?: number | null
  score_prix?: number | null
  score_potentiel?: number | null
  loyer_estime?: number | null
  rentabilite_brute?: number | null
  raison_score?: string | null
  risques_llm?: string[] | null
  recommandation?: 'fort_potentiel' | 'a_surveiller' | 'rejeter' | null
  scored_at?: string | null
}

export interface AuctionQuickLaunchPayload {
  audience_urls?: string[]
  auto_dispatch?: boolean
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
  capital?: number
  siege_social?: string
  gerant_nom?: string
  gerant_prenom?: string
  date_creation?: string
}

export interface BienFormData {
  sci_id: number
  adresse: string
  complement_adresse?: string
  ville: string
  code_postal: string
  type_bien: string
  surface?: number
  nb_pieces?: number
  etage?: number
  dpe_classe?: string | null
  dpe_date_validite?: string | null
  prix_acquisition?: number
  date_acquisition?: string | null
  valeur_actuelle?: number
  statut: string
}

export interface BailFormData {
  bien_id: number
  date_debut: string
  date_fin?: string | null
  loyer_mensuel: number
  charges_mensuelles: number
  depot_garantie?: number
}

export interface LocataireFormData {
  prenom: string
  nom: string
  email: string
  telephone?: string | null
  date_naissance?: string | null
  profession?: string | null
  revenus_annuels?: number
  bail?: BailFormData
}

// ─── User Management ──────────────────────────────────────────────────────────

export type UserRole = 'admin' | 'user' | 'readonly'

export interface AppUser {
  id: number
  email: string
  nom?: string | null
  prenom?: string | null
  role: UserRole
  is_active: boolean
  created_at: string
  last_login?: string | null
}

export interface UserCreateData {
  email: string
  password: string
  nom?: string
  prenom?: string
  role: UserRole
}

export interface UserUpdateData {
  role?: UserRole
  is_active?: boolean
}
