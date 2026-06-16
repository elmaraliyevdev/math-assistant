import { useEffect } from 'react'

import { useMe } from '@/features/auth/use-auth'
import { useOrganizationStore } from '@/stores/organization-store'

export function useSyncOrganization() {
  const { data: me } = useMe()
  const currentOrganizationId = useOrganizationStore(
    (state) => state.currentOrganizationId,
  )
  const setCurrentOrganizationId = useOrganizationStore(
    (state) => state.setCurrentOrganizationId,
  )

  useEffect(() => {
    if (!me?.organizations.length) {
      return
    }

    const stillMember = me.organizations.some(
      (org) => org.organizationId === currentOrganizationId,
    )

    if (!currentOrganizationId || !stillMember) {
      setCurrentOrganizationId(me.organizations[0].organizationId)
    }
  }, [me, currentOrganizationId, setCurrentOrganizationId])
}

export function useCurrentOrganization() {
  const { data: me } = useMe()
  const currentOrganizationId = useOrganizationStore(
    (state) => state.currentOrganizationId,
  )

  return me?.organizations.find(
    (org) => org.organizationId === currentOrganizationId,
  )
}
