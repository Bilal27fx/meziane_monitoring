'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api/client'
import type {
  Opportunite,
  CeleryTask,
  OpportuniteParams,
  AgentConfig,
  AuctionAgentRun,
  AuctionAgentRunEvent,
  AuctionListing,
  AuctionQuickLaunchPayload,
} from '@/lib/types'

export function useOpportunites(params?: OpportuniteParams) {
  return useQuery({
    queryKey: ['opportunites', params],
    queryFn: async () => {
      const response = await api.get<Opportunite[]>('/api/agent/opportunites', { params })
      return response.data
    },
    refetchInterval: 60_000,
  })
}

export function useMarkOpportuniteVue() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => api.post(`/api/agent/opportunites/${id}/vue`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['opportunites'] }),
  })
}

export function useTasks() {
  return useQuery({
    queryKey: ['tasks'],
    queryFn: async () => {
      const response = await api.get<CeleryTask[]>('/api/agent/tasks')
      return response.data
    },
    refetchInterval: 15_000,
  })
}

export function useLaunchTask() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (taskId: string) => api.post(`/api/agent/tasks/${taskId}/run`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['tasks'] }),
  })
}

export function useLogs() {
  return useQuery({
    queryKey: ['logs'],
    queryFn: async () => {
      const response = await api.get<{ time: string; level: string; module: string; message: string }[]>('/api/agent/logs')
      return response.data
    },
    refetchInterval: 5_000,
  })
}

export function useAgentConfig() {
  return useQuery({
    queryKey: ['agent-config'],
    queryFn: async () => {
      const response = await api.get<AgentConfig>('/api/agent/config')
      return response.data
    },
  })
}

export function useSaveAgentConfig() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (config: AgentConfig) => api.put('/api/agent/config', config),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['agent-config'] }),
  })
}

export function useAuctionAgentRuns() {
  return useQuery({
    queryKey: ['auction-agent-runs'],
    queryFn: async () => {
      const response = await api.get<AuctionAgentRun[]>('/api/auction-agents/runs')
      return response.data
    },
    refetchInterval: 5_000,
  })
}

export function useAuctionAgentRunEvents(runId: number | null) {
  return useQuery({
    queryKey: ['auction-agent-runs', runId, 'events'],
    queryFn: async () => {
      const response = await api.get<AuctionAgentRunEvent[]>(`/api/auction-agents/run/${runId}/events`)
      return response.data
    },
    enabled: runId !== null,
    refetchInterval: 5_000,
  })
}

export function useAuctionListings(sourceCode: string | null) {
  return useQuery({
    queryKey: ['auction-listings', sourceCode],
    queryFn: async () => {
      const response = await api.get<AuctionListing[]>('/api/auction-data/listings', {
        params: { limit: 500 },
      })
      return response.data
    },
    enabled: sourceCode !== null,
    refetchInterval: 5_000,
  })
}

export function useLaunchLicitorAuctionRun() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: AuctionQuickLaunchPayload) => {
      const response = await api.post<{ run_id: number; dispatched: boolean; task_name?: string | null }>(
        '/api/auction-agents/launch/licitor',
        payload
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['auction-agent-runs'] })
    },
  })
}
