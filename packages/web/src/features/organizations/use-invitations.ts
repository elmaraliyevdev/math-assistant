import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { authKeys } from '@/features/auth/use-auth'
import { organizationKeys } from '@/features/organizations/use-organizations'
import { invitationsService } from '@/services/invitations'

export const invitationKeys = {
  mine: ['invitations', 'mine'] as const,
  organization: (organizationId: string) =>
    ['invitations', 'organization', organizationId] as const,
}

export function useMyInvitations() {
  return useQuery({
    queryKey: invitationKeys.mine,
    queryFn: () => invitationsService.listMine(),
  })
}

export function useOrganizationInvitations(organizationId: string | null) {
  return useQuery({
    queryKey: invitationKeys.organization(organizationId ?? ''),
    queryFn: () => invitationsService.listForOrganization(organizationId!),
    enabled: Boolean(organizationId),
  })
}

export function useInviteMember(organizationId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (input: Parameters<typeof invitationsService.invite>[1]) =>
      invitationsService.invite(organizationId, input),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: invitationKeys.organization(organizationId),
      })
    },
  })
}

export function useCancelInvitation(organizationId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (invitationId: string) =>
      invitationsService.cancel(organizationId, invitationId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: invitationKeys.organization(organizationId),
      })
    },
  })
}

export function useAcceptInvitation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: invitationsService.accept,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: invitationKeys.mine })
      await queryClient.invalidateQueries({ queryKey: organizationKeys.all })
      await queryClient.invalidateQueries({ queryKey: authKeys.me })
    },
  })
}

export function useDeclineInvitation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: invitationsService.decline,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: invitationKeys.mine })
    },
  })
}
