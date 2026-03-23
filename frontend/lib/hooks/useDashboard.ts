'use client'

import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api/client'
import type { DashboardFull } from '@/lib/types'

// ─── Mock data ───────────────────────────────────────────────────────────────

function generateCashflowHistory() {
  const now = new Date()
  return Array.from({ length: 30 }, (_, i) => {
    const d = new Date(now)
    d.setDate(d.getDate() - (29 - i))
    const base = 4200
    const noise = (Math.sin(i * 0.7) * 800) + (Math.random() * 400 - 200)
    return { date: d.toISOString().split('T')[0], value: Math.round(base + noise) }
  })
}

function generatePatrimoineHistory() {
  return Array.from({ length: 12 }, (_, i) => {
    const d = new Date(2025, i, 1)
    const base = 2_200_000 + (i * 18_000) + (Math.random() * 15_000 - 7_500)
    return { date: d.toISOString().split('T')[0], value: Math.round(base) }
  })
}

const MOCK_DASHBOARD: DashboardFull = {
  kpis: {
    patrimoine_net: 2_387_500,
    patrimoine_net_change: 3.2,
    cashflow_mensuel: 4_215,
    cashflow_mensuel_change: 1.8,
    taux_occupation: 91.7,
    taux_occupation_change: -0.5,
    nb_biens: 7,
    nb_biens_change: 0,
  },
  cashflow_history: generateCashflowHistory(),
  patrimoine_history: generatePatrimoineHistory(),
  top_biens: [
    { id: 1, adresse: '12 Rue du Commerce, Paris 15e', sci_nom: 'SCI Facha', valeur: 420_000, tri_net: 8.2, rank: 1 },
    { id: 2, adresse: '7 Av. Jean Jaurès, Lyon 3e', sci_nom: 'SCI La Renaissance', valeur: 285_000, tri_net: 6.7, rank: 2 },
    { id: 3, adresse: '3 Bd de la Paix, Bordeaux', sci_nom: 'SCI Facha', valeur: 195_000, tri_net: 5.1, rank: 3 },
    { id: 4, adresse: '18 Rue Ampère, Paris 17e', sci_nom: 'SCI Patrimoine+', valeur: 510_000, tri_net: 4.2, rank: 4 },
  ],
  recent_transactions: [
    { id: 1, sci_id: 1, libelle: 'Loyer janvier — Commerce', categorie: 'Loyer', montant: 1_450, date: '2026-01-05', statut: 'valide', type: 'revenu', created_at: '', updated_at: '' },
    { id: 2, sci_id: 2, libelle: 'Charges copropriété T4 2025', categorie: 'Charges', montant: -320, date: '2026-01-03', statut: 'valide', type: 'depense', created_at: '', updated_at: '' },
    { id: 3, sci_id: 1, libelle: 'Loyer janvier — Studio', categorie: 'Loyer', montant: 820, date: '2026-01-04', statut: 'valide', type: 'revenu', created_at: '', updated_at: '' },
    { id: 4, sci_id: 3, libelle: 'Taxe foncière 2025', categorie: 'Taxe', montant: -1_240, date: '2025-12-28', statut: 'valide', type: 'depense', created_at: '', updated_at: '' },
    { id: 5, sci_id: 2, libelle: 'Loyer décembre — T3', categorie: 'Loyer', montant: 1_100, date: '2025-12-05', statut: 'valide', type: 'revenu', created_at: '', updated_at: '' },
    { id: 6, sci_id: 1, libelle: 'Assurance PNO annuelle', categorie: 'Assurance', montant: -680, date: '2025-12-15', statut: 'en_attente', type: 'depense', created_at: '', updated_at: '' },
    { id: 7, sci_id: 3, libelle: 'Honoraires agence', categorie: 'Frais', montant: -900, date: '2025-12-20', statut: 'valide', type: 'depense', created_at: '', updated_at: '' },
  ],
  sci_overview: [
    { id: 1, nom: 'SCI Facha', cashflow_mensuel: 2_150, nb_biens: 3, valeur_totale: 910_000 },
    { id: 2, nom: 'SCI La Renaissance', cashflow_mensuel: 1_320, nb_biens: 2, valeur_totale: 685_000 },
    { id: 3, nom: 'SCI Patrimoine+', cashflow_mensuel: 745, nb_biens: 2, valeur_totale: 792_500 },
  ],
  opportunites_count: 12,
  locataires_actifs: 6,
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

export function useFullDashboard() {
  return useQuery<DashboardFull>({
    queryKey: ['dashboard', 'full'],
    queryFn: async () => {
      try {
        const response = await api.get<DashboardFull>('/api/dashboard/full')
        return response.data
      } catch {
        // Fall back to mock data when API is unavailable
        return MOCK_DASHBOARD
      }
    },
    refetchInterval: 30_000,
    staleTime: 20_000,
  })
}
