'use client'

import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api/client'
import type { DashboardFull, LocataireOverview, OpportuniteOverview } from '@/lib/types'

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
  return useQuery<LocataireOverview[]>({
    queryKey: ['dashboard', 'locataires'],
    queryFn: async () => {
      const response = await api.get<{ data: LocataireOverview[] }>('/api/dashboard/locataires')
      return response.data.data
    },
    refetchInterval: 30_000,
    staleTime: 20_000,
  })
}

export function useDashboardOpportunites(limit = 2) {
  return useQuery<OpportuniteOverview[]>({
    queryKey: ['dashboard', 'opportunites', limit],
    queryFn: async () => {
      const response = await api.get<{ data: OpportuniteOverview[] }>('/api/dashboard/opportunites', {
        params: { limit },
      })
      return response.data.data
    },
    refetchInterval: 60_000,
    staleTime: 30_000,
  })
}
