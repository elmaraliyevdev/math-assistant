import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { authKeys } from '@/features/auth/use-auth'
import { organizationsService } from '@/services/organizations'
import { useOrganizationStore } from '@/stores/organization-store'
import { useCurrentOrganization } from '@/hooks/use-sync-organization'

export const organizationKeys = {
  all: ['organizations'] as const,
  detail: (organizationId: string) =>
    ['organizations', 'detail', organizationId] as const,
  members: (organizationId: string) =>
    ['organizations', 'members', organizationId] as const,
}

export function useOrganizations() {
  return useQuery({
    queryKey: organizationKeys.all,
    queryFn: () => organizationsService.list(),
  })
}

export function useOrganization(organizationId: string | null) {
  return useQuery({
    queryKey: organizationKeys.detail(organizationId ?? ''),
    queryFn: () => organizationsService.get(organizationId!),
    enabled: Boolean(organizationId),
  })
}

export function useCurrentOrganizationId() {
  const stored = useOrganizationStore((state) => state.currentOrganizationId)
  const setCurrentOrganizationId = useOrganizationStore(
    (state) => state.setCurrentOrganizationId,
  )

  return { organizationId: stored, setCurrentOrganizationId }
}

export function useCreateOrganization() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: organizationsService.create,
    onSuccess: async (organization) => {
      useOrganizationStore.getState().setCurrentOrganizationId(organization.id)
      await queryClient.invalidateQueries({ queryKey: organizationKeys.all })
      await queryClient.invalidateQueries({ queryKey: authKeys.me })
    },
  })
}

export function useUpdateOrganization(organizationId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (input: Parameters<typeof organizationsService.update>[1]) =>
      organizationsService.update(organizationId, input),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: organizationKeys.detail(organizationId),
      })
      await queryClient.invalidateQueries({ queryKey: authKeys.me })
    },
  })
}

export function useAddOrganizationMember(organizationId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (input: Parameters<typeof organizationsService.addMember>[1]) =>
      organizationsService.addMember(organizationId, input),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: authKeys.me })
    },
  })
}

export function useRemoveOrganizationMember(organizationId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (userId: string) =>
      organizationsService.removeMember(organizationId, userId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: authKeys.me })
      await queryClient.invalidateQueries({
        queryKey: organizationKeys.members(organizationId),
      })
    },
  })
}

export function useOrganizationMembers(organizationId: string | null) {
  return useQuery({
    queryKey: organizationKeys.members(organizationId ?? ''),
    queryFn: () => organizationsService.listMembers(organizationId!),
    enabled: Boolean(organizationId),
  })
}

export function useTransferOwnership(organizationId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (newOwnerUserId: string) =>
      organizationsService.transferOwnership(organizationId, newOwnerUserId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: authKeys.me })
      await queryClient.invalidateQueries({
        queryKey: organizationKeys.members(organizationId),
      })
    },
  })
}

export function useOrganizationPermissions() {
  const currentOrg = useCurrentOrganization()
  return {
    role: currentOrg?.role,
    organizationId: currentOrg?.organizationId,
  }
}
