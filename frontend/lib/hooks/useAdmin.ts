'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api/client'
import type {
  SCI, Bien, Locataire, Transaction, Quittance, Document,
  SCIParams, BienParams, LocataireParams, TransactionParams,
  SCIFormData, BienFormData, LocataireFormData,
  PaginatedResponse, BailFormData, TypeDocument,
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

// ─── Quittance Hooks ──────────────────────────────────────────────────────────

// ─── Document Hooks ───────────────────────────────────────────────────────────

export function useDocumentsSCI(sciId: number | null) {
  return useQuery({
    queryKey: ['documents', 'sci', sciId],
    queryFn: async () => {
      if (!sciId) return []
      const response = await api.get<Document[]>(`/api/documents/sci/${sciId}`)
      return response.data
    },
    enabled: !!sciId,
  })
}

export function useDocumentsBien(bienId: number | null) {
  return useQuery({
    queryKey: ['documents', 'bien', bienId],
    queryFn: async () => {
      if (!bienId) return []
      const response = await api.get<Document[]>(`/api/documents/bien/${bienId}`)
      return response.data
    },
    enabled: !!bienId,
  })
}

export function useDocumentsLocataire(locataireId: number | null) {
  return useQuery({
    queryKey: ['documents', 'locataire', locataireId],
    queryFn: async () => {
      if (!locataireId) return []
      const response = await api.get<Document[]>(`/api/documents/locataire/${locataireId}`)
      return response.data
    },
    enabled: !!locataireId,
  })
}

export function useUploadDocument() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ sciId, bienId, file, typeDocument }: { sciId: number; bienId?: number; file: File; typeDocument: TypeDocument }) => {
      const fd = new FormData()
      fd.append('sci_id', String(sciId))
      fd.append('type_document', typeDocument)
      fd.append('file', file)
      if (bienId) fd.append('bien_id', String(bienId))
      return api.post<Document>('/api/documents/upload', fd, { headers: { 'Content-Type': undefined } })
    },
    onSuccess: (_, vars) => {
      queryClient.invalidateQueries({ queryKey: ['documents', 'sci', vars.sciId] })
      if (vars.bienId) queryClient.invalidateQueries({ queryKey: ['documents', 'bien', vars.bienId] })
    },
  })
}

export function useUploadDocumentLocataire() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ locataireId, file, typeDocument }: { locataireId: number; file: File; typeDocument: TypeDocument }) => {
      const fd = new FormData()
      fd.append('locataire_id', String(locataireId))
      fd.append('type_document', typeDocument)
      fd.append('file', file)
      return api.post<Document>('/api/documents/upload-locataire', fd, { headers: { 'Content-Type': undefined } })
    },
    onSuccess: (_, vars) => queryClient.invalidateQueries({ queryKey: ['documents', 'locataire', vars.locataireId] }),
  })
}

export function useDeleteDocument() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => api.delete(`/api/documents/${id}`),
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

export function useGenerateQuittance() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (locataireId: number) =>
      api.post(`/api/locataires/${locataireId}/quittances/generer`),
    onSuccess: (_, locataireId) =>
      queryClient.invalidateQueries({ queryKey: ['quittances', locataireId] }),
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
