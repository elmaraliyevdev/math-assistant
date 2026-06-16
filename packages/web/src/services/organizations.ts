import { api } from '@/services/api'
import type {
  Organization,
  OrganizationListResponse,
  OrganizationMember,
  OrganizationMemberListResponse,
  OrganizationRole,
} from '@/types/api'

export interface CreateOrganizationInput {
  name: string
  slug: string
}

export interface UpdateOrganizationInput {
  name?: string
  slug?: string
}

export interface AddMemberInput {
  userId: string
  role: OrganizationRole
}

export const organizationsService = {
  async list(): Promise<OrganizationListResponse> {
    const { data } = await api.get<OrganizationListResponse>('/organizations')
    return data
  },

  async get(organizationId: string): Promise<Organization> {
    const { data } = await api.get<Organization>(
      `/organizations/${organizationId}`,
    )
    return data
  },

  async create(input: CreateOrganizationInput): Promise<Organization> {
    const { data } = await api.post<Organization>('/organizations', input)
    return data
  },

  async update(
    organizationId: string,
    input: UpdateOrganizationInput,
  ): Promise<Organization> {
    const { data } = await api.patch<Organization>(
      `/organizations/${organizationId}`,
      input,
    )
    return data
  },

  async addMember(
    organizationId: string,
    input: AddMemberInput,
  ): Promise<OrganizationMember> {
    const { data } = await api.post<OrganizationMember>(
      `/organizations/${organizationId}/members`,
      input,
    )
    return data
  },

  async removeMember(organizationId: string, userId: string): Promise<void> {
    await api.delete(`/organizations/${organizationId}/members/${userId}`)
  },

  async listMembers(organizationId: string): Promise<OrganizationMemberListResponse> {
    const { data } = await api.get<OrganizationMemberListResponse>(
      `/organizations/${organizationId}/members`,
    )
    return data
  },

  async transferOwnership(
    organizationId: string,
    newOwnerUserId: string,
  ): Promise<OrganizationMemberListResponse> {
    const { data } = await api.post<OrganizationMemberListResponse>(
      `/organizations/${organizationId}/transfer-ownership`,
      { newOwnerUserId },
    )
    return data
  },
}
