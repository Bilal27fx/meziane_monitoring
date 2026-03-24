'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api/client'
import type { Opportunite, CeleryTask, OpportuniteParams, AgentConfig } from '@/lib/types'

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
