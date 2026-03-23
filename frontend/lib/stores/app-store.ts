import { create } from 'zustand'

type AdminTab = 'sci' | 'biens' | 'locataires' | 'transactions' | 'systeme'
type AgentTab = 'prospection' | 'taches' | 'logs'

interface ModalState {
  type: string
  data?: unknown
}

interface AppStore {
  // Tab state
  adminTab: AdminTab
  agentTab: AgentTab
  setAdminTab: (tab: AdminTab) => void
  setAgentTab: (tab: AgentTab) => void

  // Modal state
  modal: ModalState | null
  openModal: (type: string, data?: unknown) => void
  closeModal: () => void

  // Selection state for panels
  selectedLocataireId: number | null
  selectedBienId: number | null
  setSelectedLocataireId: (id: number | null) => void
  setSelectedBienId: (id: number | null) => void

  // Panel open state
  quittancesPanelOpen: boolean
  setQuittancesPanelOpen: (open: boolean) => void
}

export const useAppStore = create<AppStore>((set) => ({
  // Tab state
  adminTab: 'sci',
  agentTab: 'prospection',
  setAdminTab: (tab) => set({ adminTab: tab }),
  setAgentTab: (tab) => set({ agentTab: tab }),

  // Modal state
  modal: null,
  openModal: (type, data) => set({ modal: { type, data } }),
  closeModal: () => set({ modal: null }),

  // Selection state
  selectedLocataireId: null,
  selectedBienId: null,
  setSelectedLocataireId: (id) => set({ selectedLocataireId: id }),
  setSelectedBienId: (id) => set({ selectedBienId: id }),

  // Panel state
  quittancesPanelOpen: false,
  setQuittancesPanelOpen: (open) => set({ quittancesPanelOpen: open }),
}))
