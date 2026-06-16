import { api } from '@/services/api'
import type {
  OrganizationInvitation,
  OrganizationInvitationListResponse,
  OrganizationRole,
} from '@/types/api'

export interface InviteMemberInput {
  email: string
  role: Exclude<OrganizationRole, 'owner'>
}

export const invitationsService = {
  async listMine(): Promise<OrganizationInvitationListResponse> {
    const { data } = await api.get<OrganizationInvitationListResponse>(
      '/invitations/mine',
    )
    return data
  },

  async listForOrganization(
    organizationId: string,
  ): Promise<OrganizationInvitationListResponse> {
    const { data } = await api.get<OrganizationInvitationListResponse>(
      `/organizations/${organizationId}/invitations`,
    )
    return data
  },

  async invite(
    organizationId: string,
    input: InviteMemberInput,
  ): Promise<OrganizationInvitation> {
    const { data } = await api.post<OrganizationInvitation>(
      `/organizations/${organizationId}/invitations`,
      input,
    )
    return data
  },

  async cancel(organizationId: string, invitationId: string): Promise<void> {
    await api.delete(
      `/organizations/${organizationId}/invitations/${invitationId}`,
    )
  },

  async accept(invitationId: string): Promise<OrganizationInvitation> {
    const { data } = await api.post<OrganizationInvitation>(
      `/invitations/${invitationId}/accept`,
    )
    return data
  },

  async decline(invitationId: string): Promise<OrganizationInvitation> {
    const { data } = await api.post<OrganizationInvitation>(
      `/invitations/${invitationId}/decline`,
    )
    return data
  },
}
