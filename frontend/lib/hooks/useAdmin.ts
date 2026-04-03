'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api/client'
import type {
  SCI, Bien, Locataire, Transaction, Quittance, Document,
  DocumentFolder, DocumentLibrary,
  LocatairePaiementOverview,
  SCIParams, BienParams, LocataireParams, TransactionParams,
  SCIFormData, BienFormData, LocataireFormData,
  PaginatedResponse, BailFormData,
  AppUser, UserCreateData, UserUpdateData,
} from '@/lib/types'

// ─── SCI Hooks ────────────────────────────────────────────────────────────────

export function useSCIs(params?: SCIParams) {
  return useQuery({
    queryKey: ['scis', params],
    queryFn: async () => {
      const response = await api.get<PaginatedResponse<SCI>>('/api/sci', { params })
      return response.data
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
      const response = await api.get<PaginatedResponse<Bien>>('/api/biens', { params })
      return response.data
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
      const response = await api.get<PaginatedResponse<Locataire>>('/api/locataires', { params })
      return response.data
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
      const response = await api.get<PaginatedResponse<Transaction>>('/api/transactions', { params })
      return response.data
    },
  })
}

export function useValidateTransaction() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => api.post(`/api/transactions/${id}/valider`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['transactions'] }),
  })
}

export function useRejectTransaction() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => api.post(`/api/transactions/${id}/rejeter`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['transactions'] }),
  })
}

export function useCreateTransaction() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: {
      date: string; montant: number; libelle: string
      compte_bancaire_id: string; sci_id: number; categorie?: string
    }) => api.post('/api/transactions', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['transactions'] }),
  })
}

export function useUpdateTransaction() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: {
      date?: string; montant?: number; libelle?: string; categorie?: string
    }}) => api.put(`/api/transactions/${id}`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['transactions'] }),
  })
}

export function useDeleteTransaction() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => api.delete(`/api/transactions/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard', 'full'] })
    },
  })
}

// ─── Quittance Hooks ──────────────────────────────────────────────────────────

// ─── Document Hooks ───────────────────────────────────────────────────────────

export function useDocumentLibrary(params: {
  sciId?: number | null
  bienId?: number | null
  locataireId?: number | null
  folderId?: number | null
}) {
  return useQuery({
    queryKey: ['documents', 'library', params],
    queryFn: async () => {
      const response = await api.get<DocumentLibrary>('/api/documents/library', {
        params: {
          sci_id: params.sciId ?? undefined,
          bien_id: params.bienId ?? undefined,
          locataire_id: params.locataireId ?? undefined,
          folder_id: params.folderId ?? undefined,
        },
      })
      return response.data
    },
    enabled: Boolean(params.sciId || params.bienId || params.locataireId || params.folderId),
  })
}

export function useUploadDocument() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({
      sciId,
      bienId,
      locataireId,
      folderId,
      file,
      nomDocument,
    }: {
      sciId?: number
      bienId?: number
      locataireId?: number
      folderId?: number
      file: File
      nomDocument?: string
    }) => {
      const fd = new FormData()
      if (sciId) fd.append('sci_id', String(sciId))
      if (bienId) fd.append('bien_id', String(bienId))
      if (locataireId) fd.append('locataire_id', String(locataireId))
      if (folderId) fd.append('folder_id', String(folderId))
      fd.append('type_document', 'autre')
      if (nomDocument) fd.append('nom_document', nomDocument)
      fd.append('file', file)
      return api.post<Document>('/api/documents/upload', fd, { headers: { 'Content-Type': undefined } })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
  })
}

export function useCreateDocumentFolder() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: {
      sciId?: number
      bienId?: number
      locataireId?: number
      parentId?: number
      nom: string
    }) =>
      api.post<DocumentFolder>('/api/documents/folders', {
        sci_id: data.sciId,
        bien_id: data.bienId,
        locataire_id: data.locataireId,
        parent_id: data.parentId,
        nom: data.nom,
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['documents'] }),
  })
}

export function useDeleteDocument() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => api.delete(`/api/documents/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['documents'] }),
  })
}

export function useDeleteDocumentFolder() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => api.delete(`/api/documents/folders/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['documents'] }),
  })
}

// ─── User Hooks ───────────────────────────────────────────────────────────────

export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const response = await api.get<AppUser[]>('/api/users')
      return response.data
    },
  })
}

export function useCreateUser() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: UserCreateData) => api.post<AppUser>('/api/users', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['users'] }),
  })
}

export function useUpdateUser() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UserUpdateData }) =>
      api.put<AppUser>(`/api/users/${id}`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['users'] }),
  })
}

export function useDeleteUser() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => api.delete(`/api/users/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['users'] }),
  })
}

export function useMarkQuittancePaid() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (quittanceId: number) =>
      api.post<Quittance>(`/api/quittances/${quittanceId}/payer`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['quittances'] })
      queryClient.invalidateQueries({ queryKey: ['locataire-payments'] })
      queryClient.invalidateQueries({ queryKey: ['locataires'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard', 'full'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard', 'locataires'] })
    },
  })
}

export function useQuittances(locataireId: number | null) {
  return useQuery({
    queryKey: ['quittances', locataireId],
    queryFn: async () => {
      if (!locataireId) return []
      const response = await api.get<Quittance[]>(`/api/locataires/${locataireId}/quittances`)
      return response.data
    },
    enabled: !!locataireId,
  })
}

export function useLocatairePayments(locataireId: number | null) {
  return useQuery({
    queryKey: ['locataire-payments', locataireId],
    queryFn: async () => {
      if (!locataireId) return null
      const response = await api.get<LocatairePaiementOverview>(`/api/locataires/${locataireId}/paiements`)
      const data = response.data
      return {
        ...data,
        paiements: data.paiements ?? [],
        derniers_mois: data.derniers_mois ?? [],
        historique_mensuel: data.historique_mensuel ?? data.derniers_mois ?? [],
        resume_annuel: data.resume_annuel ?? [],
      }
    },
    enabled: !!locataireId,
  })
}

export function useCreateLocatairePayment() {
  const queryClient = useQueryClient()
  type LocatairePaymentPayload = {
    locataireId: number
    data: {
      montant: number
      date_paiement: string
      mode_paiement?: 'virement' | 'prelevement' | 'carte' | 'cheque' | 'especes' | 'autre'
      quittance_id?: number
      periode_key?: string
      reference?: string
      note?: string
    }
  }
  return useMutation({
    mutationFn: ({ locataireId, data }: LocatairePaymentPayload) =>
      api.post(`/api/locataires/${locataireId}/paiements`, data),
    onSuccess: (_: unknown, vars: LocatairePaymentPayload) => {
      queryClient.invalidateQueries({ queryKey: ['locataire-payments', vars.locataireId] })
      queryClient.invalidateQueries({ queryKey: ['quittances', vars.locataireId] })
      queryClient.invalidateQueries({ queryKey: ['quittances'] })
      queryClient.invalidateQueries({ queryKey: ['locataires'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard', 'full'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard', 'locataires'] })
    },
  })
}
