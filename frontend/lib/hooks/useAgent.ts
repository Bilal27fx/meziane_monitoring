'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api/client'
import type { Opportunite, CeleryTask, OpportuniteParams, AgentConfig } from '@/lib/types'

// ─── Mock data ─────────────────────────────────────────────────────────────────

const MOCK_OPPORTUNITES: Opportunite[] = [
  {
    id: 1,
    adresse: '42 Rue Marcadet',
    ville: 'Paris 18e',
    prix: 310_000,
    surface: 38,
    nb_pieces: 2,
    dpe: 'C',
    tri_estime: 7.8,
    score: 92,
    statut: 'nouveau',
    source: 'SeLoger',
    url: 'https://seloger.com',
    analyse_ia: "Excellent rapport qualité/prix pour ce quartier. La demande locative est forte dans le 18e arrondissement avec un taux de vacance inférieur à 2%. Le DPE C garantit la conformité réglementaire jusqu'en 2034. Potentiel de plus-value estimé à 15% sur 5 ans.",
    risques: ['Proximité Bd Ornano — nuisances sonores possibles', 'Bâtiment années 1960 — prévoir budget travaux'],
    created_at: '2026-01-15T10:23:00Z',
    updated_at: '2026-01-15T10:23:00Z',
  },
  {
    id: 2,
    adresse: '18 Cours Lafayette',
    ville: 'Lyon 3e',
    prix: 245_000,
    surface: 55,
    nb_pieces: 3,
    dpe: 'B',
    tri_estime: 6.4,
    score: 87,
    statut: 'nouveau',
    source: 'PAP',
    url: 'https://pap.fr',
    analyse_ia: "Bien bien positionné dans le 3e arrondissement de Lyon, secteur prisé par les jeunes actifs. Le DPE B est un atout majeur. Prix légèrement au-dessus du marché mais compensé par la qualité du bien.",
    risques: ['Prix légèrement surévalué vs. marché local'],
    created_at: '2026-01-14T14:00:00Z',
    updated_at: '2026-01-14T14:00:00Z',
  },
  {
    id: 3,
    adresse: '7 Rue Nationale',
    ville: 'Bordeaux Centre',
    prix: 185_000,
    surface: 42,
    nb_pieces: 2,
    dpe: 'D',
    tri_estime: 5.9,
    score: 74,
    statut: 'vu',
    source: 'LeBonCoin',
    created_at: '2026-01-13T09:15:00Z',
    updated_at: '2026-01-13T09:15:00Z',
  },
  {
    id: 4,
    adresse: '29 Rue de la Paix',
    ville: 'Nantes',
    prix: 220_000,
    surface: 60,
    nb_pieces: 3,
    dpe: 'C',
    tri_estime: 5.4,
    score: 68,
    statut: 'vu',
    source: 'SeLoger',
    created_at: '2026-01-12T16:30:00Z',
    updated_at: '2026-01-12T16:30:00Z',
  },
  {
    id: 5,
    adresse: '5 Impasse des Lilas',
    ville: 'Marseille 8e',
    prix: 160_000,
    surface: 50,
    nb_pieces: 2,
    dpe: 'E',
    tri_estime: 4.8,
    score: 55,
    statut: 'vu',
    source: 'PAP',
    created_at: '2026-01-11T11:00:00Z',
    updated_at: '2026-01-11T11:00:00Z',
  },
]

const MOCK_TASKS: CeleryTask[] = [
  { id: 'task-1', name: 'scrape_seloger', statut: 'ok', derniere_exec: '2026-01-15T06:00:00Z', prochaine_exec: '2026-01-16T06:00:00Z', tasks_24h: 24, succes: 23, erreurs: 1, en_attente: 0 },
  { id: 'task-2', name: 'scrape_pap', statut: 'ok', derniere_exec: '2026-01-15T06:05:00Z', prochaine_exec: '2026-01-16T06:05:00Z', tasks_24h: 12, succes: 12, erreurs: 0, en_attente: 0 },
  { id: 'task-3', name: 'analyse_opportunites', statut: 'warning', derniere_exec: '2026-01-15T07:00:00Z', prochaine_exec: '2026-01-16T07:00:00Z', tasks_24h: 8, succes: 6, erreurs: 2, en_attente: 3 },
  { id: 'task-4', name: 'generate_quittances', statut: 'ok', derniere_exec: '2026-01-01T00:00:00Z', prochaine_exec: '2026-02-01T00:00:00Z', tasks_24h: 1, succes: 1, erreurs: 0, en_attente: 0 },
]

const MOCK_LOGS = [
  { time: '09:42:15', level: 'INFO', module: 'scraper.seloger', message: 'Démarrage scraping SeLoger — Paris 18e, Lyon 3e' },
  { time: '09:42:18', level: 'DEBUG', module: 'http.client', message: 'GET https://www.seloger.com/list.htm?... → 200 OK (1.2s)' },
  { time: '09:42:22', level: 'INFO', module: 'scraper.seloger', message: '47 annonces récupérées, 12 nouvelles détectées' },
  { time: '09:42:25', level: 'INFO', module: 'analyser.ia', message: 'Analyse IA en cours pour 12 opportunités...' },
  { time: '09:42:31', level: 'DEBUG', module: 'analyser.ia', message: 'Score calculé: Paris 18e Rue Marcadet → 92/100' },
  { time: '09:42:35', level: 'DEBUG', module: 'analyser.ia', message: 'Score calculé: Lyon 3e Cours Lafayette → 87/100' },
  { time: '09:42:38', level: 'INFO', module: 'analyser.ia', message: '12 analyses terminées en 13.2s' },
  { time: '09:43:00', level: 'INFO', module: 'scraper.pap', message: 'Démarrage scraping PAP — budget max 350K€' },
  { time: '09:43:05', level: 'WARN', module: 'http.client', message: 'Rate limit PAP — attente 5s avant retry' },
  { time: '09:43:10', level: 'DEBUG', module: 'http.client', message: 'Retry #1: GET https://www.pap.fr/... → 200 OK (2.1s)' },
  { time: '09:43:15', level: 'INFO', module: 'scraper.pap', message: '23 annonces récupérées, 5 nouvelles détectées' },
  { time: '09:43:20', level: 'INFO', module: 'db.opportunites', message: '17 opportunités sauvegardées en base (5 nouvelles, 12 mises à jour)' },
  { time: '09:43:21', level: 'INFO', module: 'notif.email', message: 'Notification envoyée — 2 opportunités score > 85' },
  { time: '09:44:00', level: 'ERROR', module: 'scraper.leboncoin', message: 'ConnectionError: impossible de joindre leboncoin.fr — timeout 30s' },
  { time: '09:44:01', level: 'WARN', module: 'task.scheduler', message: 'Task scrape_leboncoin marquée en erreur, prochaine tentative dans 1h' },
  { time: '09:45:00', level: 'INFO', module: 'celery.worker', message: 'Worker beat — 0 tâches en attente' },
]

// ─── Hooks ─────────────────────────────────────────────────────────────────────

export function useOpportunites(params?: OpportuniteParams) {
  return useQuery({
    queryKey: ['opportunites', params],
    queryFn: async () => {
      try {
        const response = await api.get<Opportunite[]>('/api/agent/opportunites', { params })
        return response.data
      } catch {
        return MOCK_OPPORTUNITES
      }
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
      try {
        const response = await api.get<CeleryTask[]>('/api/agent/tasks')
        return response.data
      } catch {
        return MOCK_TASKS
      }
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
      try {
        const response = await api.get<typeof MOCK_LOGS>('/api/agent/logs')
        return response.data
      } catch {
        return MOCK_LOGS
      }
    },
    refetchInterval: 5_000,
  })
}

export function useAgentConfig() {
  return useQuery({
    queryKey: ['agent-config'],
    queryFn: async () => {
      try {
        const response = await api.get<AgentConfig>('/api/agent/config')
        return response.data
      } catch {
        return {
          villes_cibles: ['Paris 18e', 'Lyon 3e', 'Bordeaux'],
          budget_max: 400_000,
          tri_minimum: 5,
          sources: ['SeLoger', 'PAP', 'LeBonCoin'],
        } as AgentConfig
      }
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

export { MOCK_LOGS }
