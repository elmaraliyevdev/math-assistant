import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface OrganizationState {
  currentOrganizationId: string | null
  setCurrentOrganizationId: (organizationId: string) => void
  clear: () => void
}

export const useOrganizationStore = create<OrganizationState>()(
  persist(
    (set) => ({
      currentOrganizationId: null,
      setCurrentOrganizationId: (organizationId) =>
        set({ currentOrganizationId: organizationId }),
      clear: () => set({ currentOrganizationId: null }),
    }),
    { name: 'ma_current_organization' },
  ),
)
