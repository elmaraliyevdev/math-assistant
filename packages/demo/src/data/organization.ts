import type { Organization, OrganizationMemberListResponse } from '@web/types/api'

import { DEMO_ORGANIZATION_ID } from './constants'

export const demoOrganization: Organization = {
  id: DEMO_ORGANIZATION_ID,
  name: 'MathStudio Labs',
  slug: 'mathstudio-labs',
  createdAt: '2025-11-01T00:00:00Z',
  updatedAt: '2026-06-01T00:00:00Z',
}

export const demoOrganizationMembers: OrganizationMemberListResponse = {
  items: [
    {
      userId: 'user-elena',
      organizationId: DEMO_ORGANIZATION_ID,
      role: 'owner',
      email: 'elena.k@mathstudio.io',
      fullName: 'Elena Kowalski',
    },
    {
      userId: 'user-marcus',
      organizationId: DEMO_ORGANIZATION_ID,
      role: 'admin',
      email: 'marcus.t@mathstudio.io',
      fullName: 'Marcus Tan',
    },
    {
      userId: 'user-sarah',
      organizationId: DEMO_ORGANIZATION_ID,
      role: 'developer',
      email: 'sarah.l@mathstudio.io',
      fullName: 'Sarah Lindqvist',
    },
    {
      userId: 'user-james',
      organizationId: DEMO_ORGANIZATION_ID,
      role: 'viewer',
      email: 'james.p@mathstudio.io',
      fullName: 'James Park',
    },
  ],
}
