'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api/client'
import type {
  SCI, Bien, Locataire, Transaction, Quittance,
  SCIParams, BienParams, LocataireParams, TransactionParams,
  SCIFormData, BienFormData, LocataireFormData,
  PaginatedResponse,
} from '@/lib/types'

// ─── Mock data fallbacks ─────────────────────────────────────────────────────

const MOCK_SCIS: SCI[] = [
  { id: 1, nom: 'SCI Facha', siret: '123 456 789 00012', forme_juridique: 'SCI', capital_social: 10_000, adresse_siege: '12 Rue du Commerce, 75015 Paris', date_creation: '2018-03-15', email: 'contact@scifacha.fr', nb_biens: 3, valeur_totale: 910_000, cashflow_mensuel: 2_150, created_at: '2024-01-01', updated_at: '2024-01-01' },
  { id: 2, nom: 'SCI La Renaissance', siret: '987 654 321 00034', forme_juridique: 'SCI', capital_social: 15_000, adresse_siege: '7 Av. Jean Jaurès, 69003 Lyon', date_creation: '2020-06-20', email: 'contact@renaissance.fr', nb_biens: 2, valeur_totale: 685_000, cashflow_mensuel: 1_320, created_at: '2024-01-01', updated_at: '2024-01-01' },
  { id: 3, nom: 'SCI Patrimoine+', siret: '456 789 123 00056', forme_juridique: 'SCI', capital_social: 20_000, adresse_siege: '3 Bd de la Paix, 33000 Bordeaux', date_creation: '2021-11-08', email: 'contact@patrimoineplus.fr', nb_biens: 2, valeur_totale: 792_500, cashflow_mensuel: 745, created_at: '2024-01-01', updated_at: '2024-01-01' },
]

const MOCK_BIENS: Bien[] = [
  { id: 1, sci_id: 1, adresse: '12 Rue du Commerce', ville: 'Paris 15e', code_postal: '75015', type: 'appartement', surface: 48, nb_pieces: 2, dpe: 'C', prix_acquisition: 385_000, valeur_actuelle: 420_000, statut: 'loue', loyer_mensuel: 1_450, tri_net: 8.2, created_at: '2024-01-01', updated_at: '2024-01-01' },
  { id: 2, sci_id: 2, adresse: '7 Av. Jean Jaurès', ville: 'Lyon 3e', code_postal: '69003', type: 'appartement', surface: 65, nb_pieces: 3, dpe: 'B', prix_acquisition: 265_000, valeur_actuelle: 285_000, statut: 'loue', loyer_mensuel: 1_100, tri_net: 6.7, created_at: '2024-01-01', updated_at: '2024-01-01' },
  { id: 3, sci_id: 1, adresse: '3 Bd de la Paix', ville: 'Bordeaux', code_postal: '33000', type: 'maison', surface: 95, nb_pieces: 4, dpe: 'D', prix_acquisition: 180_000, valeur_actuelle: 195_000, statut: 'loue', loyer_mensuel: 850, tri_net: 5.1, created_at: '2024-01-01', updated_at: '2024-01-01' },
  { id: 4, sci_id: 3, adresse: '18 Rue Ampère', ville: 'Paris 17e', code_postal: '75017', type: 'appartement', surface: 72, nb_pieces: 3, dpe: 'C', prix_acquisition: 490_000, valeur_actuelle: 510_000, statut: 'vacant', loyer_mensuel: 0, tri_net: 4.2, created_at: '2024-01-01', updated_at: '2024-01-01' },
]

const MOCK_LOCATAIRES: Locataire[] = [
  { id: 1, prenom: 'Karim', nom: 'Benzara', email: 'karim.benzara@gmail.com', telephone: '0612345678', profession: 'Ingénieur', revenus_annuels: 52_000, bien_id: 1, statut_paiement: 'a_jour', created_at: '2024-01-01', updated_at: '2024-01-01' },
  { id: 2, prenom: 'Sophie', nom: 'Durand', email: 'sophie.durand@outlook.fr', telephone: '0698765432', profession: 'Professeure', revenus_annuels: 38_000, bien_id: 2, statut_paiement: 'retard', jours_retard: 8, created_at: '2024-01-01', updated_at: '2024-01-01' },
]

const MOCK_TRANSACTIONS: Transaction[] = [
  { id: 1, sci_id: 1, libelle: 'Loyer janvier 2026', categorie: 'Loyer', montant: 1_450, date: '2026-01-05', statut: 'valide', type: 'revenu', created_at: '', updated_at: '' },
  { id: 2, sci_id: 2, libelle: 'Charges copropriété', categorie: 'Charges', montant: -320, date: '2026-01-03', statut: 'valide', type: 'depense', created_at: '', updated_at: '' },
  { id: 3, sci_id: 1, libelle: 'Loyer studio janvier', categorie: 'Loyer', montant: 820, date: '2026-01-04', statut: 'valide', type: 'revenu', created_at: '', updated_at: '' },
  { id: 4, sci_id: 3, libelle: 'Taxe foncière 2025', categorie: 'Taxe', montant: -1_240, date: '2025-12-28', statut: 'valide', type: 'depense', created_at: '', updated_at: '' },
  { id: 5, sci_id: 2, libelle: 'Loyer décembre T3', categorie: 'Loyer', montant: 1_100, date: '2025-12-05', statut: 'valide', type: 'revenu', created_at: '', updated_at: '' },
  { id: 6, sci_id: 1, libelle: 'Assurance PNO annuelle', categorie: 'Assurance', montant: -680, date: '2025-12-15', statut: 'en_attente', type: 'depense', created_at: '', updated_at: '' },
  { id: 7, sci_id: 3, libelle: 'Honoraires agence', categorie: 'Frais', montant: -900, date: '2025-12-20', statut: 'valide', type: 'depense', created_at: '', updated_at: '' },
  { id: 8, sci_id: 2, libelle: 'Travaux peinture', categorie: 'Travaux', montant: -1_800, date: '2025-11-30', statut: 'valide', type: 'depense', created_at: '', updated_at: '' },
]

// ─── SCI Hooks ────────────────────────────────────────────────────────────────

export function useSCIs(params?: SCIParams) {
  return useQuery({
    queryKey: ['scis', params],
    queryFn: async () => {
      try {
        const response = await api.get<PaginatedResponse<SCI>>('/api/sci', { params })
        return response.data
      } catch {
        return { items: MOCK_SCIS, total: MOCK_SCIS.length, page: 1, per_page: 20, pages: 1 }
      }
    },
  })
}

export function useCreateSCI() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: SCIFormData) => api.post('/api/sci', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['scis'] }),
  })
}

export function useUpdateSCI() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<SCIFormData> }) =>
      api.put(`/api/sci/${id}`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['scis'] }),
  })
}

export function useDeleteSCI() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => api.delete(`/api/sci/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['scis'] }),
  })
}

// ─── Bien Hooks ───────────────────────────────────────────────────────────────

export function useBiens(params?: BienParams) {
  return useQuery({
    queryKey: ['biens', params],
    queryFn: async () => {
      try {
        const response = await api.get<PaginatedResponse<Bien>>('/api/biens', { params })
        return response.data
      } catch {
        return { items: MOCK_BIENS, total: MOCK_BIENS.length, page: 1, per_page: 20, pages: 1 }
      }
    },
  })
}

export function useCreateBien() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: BienFormData) => api.post('/api/biens', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['biens'] }),
  })
}

export function useUpdateBien() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<BienFormData> }) =>
      api.put(`/api/biens/${id}`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['biens'] }),
  })
}

export function useDeleteBien() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => api.delete(`/api/biens/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['biens'] }),
  })
}

// ─── Locataire Hooks ──────────────────────────────────────────────────────────

export function useLocataires(params?: LocataireParams) {
  return useQuery({
    queryKey: ['locataires', params],
    queryFn: async () => {
      try {
        const response = await api.get<PaginatedResponse<Locataire>>('/api/locataires', { params })
        return response.data
      } catch {
        return { items: MOCK_LOCATAIRES, total: MOCK_LOCATAIRES.length, page: 1, per_page: 20, pages: 1 }
      }
    },
  })
}

export function useCreateLocataire() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: LocataireFormData) => api.post('/api/locataires', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['locataires'] }),
  })
}

export function useUpdateLocataire() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<LocataireFormData> }) =>
      api.put(`/api/locataires/${id}`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['locataires'] }),
  })
}

export function useDeleteLocataire() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => api.delete(`/api/locataires/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['locataires'] }),
  })
}

// ─── Transaction Hooks ────────────────────────────────────────────────────────

export function useTransactions(params?: TransactionParams) {
  return useQuery({
    queryKey: ['transactions', params],
    queryFn: async () => {
      try {
        const response = await api.get<PaginatedResponse<Transaction>>('/api/transactions', { params })
        return response.data
      } catch {
        return { items: MOCK_TRANSACTIONS, total: MOCK_TRANSACTIONS.length, page: 1, per_page: 20, pages: 1 }
      }
    },
  })
}

export function useValidateTransaction() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => api.post(`/api/transactions/${id}/validate`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['transactions'] }),
  })
}

export function useRejectTransaction() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => api.post(`/api/transactions/${id}/reject`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['transactions'] }),
  })
}

// ─── Quittance Hooks ──────────────────────────────────────────────────────────

const MOCK_QUITTANCES: Quittance[] = Array.from({ length: 6 }, (_, i) => {
  const d = new Date(2025, 11 - i, 1)
  return {
    id: i + 1,
    locataire_id: 1,
    mois: d.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' }),
    montant: 1_450,
    statut: i === 0 ? 'en_attente' : 'payee',
    date_paiement: i === 0 ? undefined : new Date(2025, 11 - i, 5).toISOString().split('T')[0],
    created_at: '',
  }
})

export function useQuittances(locataireId: number | null) {
  return useQuery({
    queryKey: ['quittances', locataireId],
    queryFn: async () => {
      if (!locataireId) return MOCK_QUITTANCES
      try {
        const response = await api.get<Quittance[]>(`/api/locataires/${locataireId}/quittances`)
        return response.data
      } catch {
        return MOCK_QUITTANCES
      }
    },
    enabled: !!locataireId || locataireId === null,
  })
}
