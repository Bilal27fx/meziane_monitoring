'use client'

import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api/client'
import type { DashboardFull, Locataire, Opportunite } from '@/lib/types'

export function useFullDashboard() {
  return useQuery<DashboardFull>({
    queryKey: ['dashboard', 'full'],
    queryFn: async () => {
      const response = await api.get<DashboardFull>('/api/dashboard/full')
      return response.data
    },
    refetchInterval: 30_000,
    staleTime: 20_000,
  })
}

export function useDashboardLocataires() {
  return useQuery<Locataire[]>({
    queryKey: ['dashboard', 'locataires'],
    queryFn: async () => {
      const response = await api.get<{ data: Locataire[] }>('/api/dashboard/locataires')
      return response.data.data
    },
    refetchInterval: 30_000,
    staleTime: 20_000,
  })
}

export function useDashboardOpportunites(limit = 2) {
  return useQuery<Opportunite[]>({
    queryKey: ['dashboard', 'opportunites', limit],
    queryFn: async () => {
      const response = await api.get<{ data: Opportunite[] }>('/api/dashboard/opportunites', {
        params: { limit },
      })
      return response.data.data
    },
    refetchInterval: 60_000,
    staleTime: 30_000,
  })
}
