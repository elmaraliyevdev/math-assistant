import type { OrganizationRole } from '@/types/api'

const ROLE_RANK: Record<OrganizationRole, number> = {
  viewer: 1,
  developer: 2,
  admin: 3,
  owner: 4,
}

export function roleAtLeast(
  role: OrganizationRole | undefined,
  minimum: OrganizationRole,
): boolean {
  if (!role) return false
  return ROLE_RANK[role] >= ROLE_RANK[minimum]
}

export function canRead(role: OrganizationRole | undefined): boolean {
  return roleAtLeast(role, 'viewer')
}

export function canWriteGames(role: OrganizationRole | undefined): boolean {
  return roleAtLeast(role, 'developer')
}

export function canManageMembers(role: OrganizationRole | undefined): boolean {
  return roleAtLeast(role, 'admin')
}

export function canManageOrganization(role: OrganizationRole | undefined): boolean {
  return roleAtLeast(role, 'owner')
}

export function canRequestReview(role: OrganizationRole | undefined): boolean {
  return roleAtLeast(role, 'developer')
}

export function canApproveReview(role: OrganizationRole | undefined): boolean {
  return roleAtLeast(role, 'admin')
}

export function canReleaseSimulation(role: OrganizationRole | undefined): boolean {
  return roleAtLeast(role, 'owner')
}

export function canRecordApproval(
  role: OrganizationRole | undefined,
  stage:
    | 'mathematician'
    | 'senior_mathematician'
    | 'product_owner'
    | 'producer',
): boolean {
  if (stage === 'producer') {
    return roleAtLeast(role, 'owner')
  }
  return roleAtLeast(role, 'admin')
}

export const PERMISSION_MESSAGES = {
  manageMembers: 'Only organization admins and owners can manage members.',
  manageOrganization: 'Only the organization owner can change organization settings.',
  writeGames: 'Developers and above can create or edit games.',
  requestReview: 'Developers and above can submit simulations for review.',
  approveReview: 'Admins and owners can approve or request changes.',
  releaseSimulation: 'Only the organization owner can release a simulation.',
  recordApproval: 'Approval stages require admin or owner permissions.',
} as const
