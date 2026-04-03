'use client'

import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api/client'
import type { ServicesHealth } from '@/lib/types'

export function useSystemHealth() {
  return useQuery<ServicesHealth>({
    queryKey: ['system', 'health'],
    queryFn: async () => {
      const response = await api.get<ServicesHealth>('/health/services')
      return response.data
    },
    refetchInterval: 30_000,
    staleTime: 20_000,
    retry: 1,
  })
}
