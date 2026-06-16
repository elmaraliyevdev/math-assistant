import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'
import { useMe } from '@/features/auth/use-auth'
import { PermissionNotice } from '@/features/organizations/components/PermissionNotice'
import { RoleBadge } from '@/features/organizations/components/RoleBadge'
import {
  useAcceptInvitation,
  useCancelInvitation,
  useInviteMember,
  useMyInvitations,
  useOrganizationInvitations,
} from '@/features/organizations/use-invitations'
import {
  useCreateOrganization,
  useOrganization,
  useOrganizationMembers,
  useOrganizationPermissions,
  useRemoveOrganizationMember,
  useTransferOwnership,
  useUpdateOrganization,
} from '@/features/organizations/use-organizations'
import { canManageMembers, canManageOrganization, PERMISSION_MESSAGES } from '@/lib/permissions'
import { getErrorMessage } from '@/services/api'
import { useOrganizationStore } from '@/stores/organization-store'
import type { OrganizationRole } from '@/types/api'

const orgSchema = z.object({
  name: z.string().min(1),
  slug: z
    .string()
    .min(1)
    .regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, 'Use lowercase letters, numbers, and hyphens'),
})

const inviteSchema = z.object({
  email: z.email(),
  role: z.enum(['admin', 'developer', 'viewer']),
})

type OrgForm = z.infer<typeof orgSchema>
type InviteForm = z.infer<typeof inviteSchema>

export function OrganizationSettingsPage() {
  const organizationId = useOrganizationStore((state) => state.currentOrganizationId)
  const { role } = useOrganizationPermissions()
  const organization = useOrganization(organizationId)
  const members = useOrganizationMembers(organizationId)
  const invitations = useOrganizationInvitations(organizationId)
  const myInvitations = useMyInvitations()
  const { data: me } = useMe()
  const createOrganization = useCreateOrganization()
  const updateOrganization = useUpdateOrganization(organizationId ?? '')
  const inviteMember = useInviteMember(organizationId ?? '')
  const cancelInvitation = useCancelInvitation(organizationId ?? '')
  const removeMember = useRemoveOrganizationMember(organizationId ?? '')
  const transferOwnership = useTransferOwnership(organizationId ?? '')
  const acceptInvitation = useAcceptInvitation()
  const [transferUserId, setTransferUserId] = useState('')

  const orgForm = useForm<OrgForm>({
    resolver: zodResolver(orgSchema),
    values: organization.data
      ? { name: organization.data.name, slug: organization.data.slug }
      : undefined,
  })

  const createOrgForm = useForm<OrgForm>({
    resolver: zodResolver(orgSchema),
    defaultValues: { name: '', slug: '' },
  })

  const inviteForm = useForm<InviteForm>({
    resolver: zodResolver(inviteSchema),
    defaultValues: { role: 'developer' },
  })

  const canManage = canManageMembers(role)
  const canEditOrg = canManageOrganization(role)

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Organization</h2>
        <p className="text-muted-foreground">
          Invite teammates, manage roles, and switch workspaces.
        </p>
      </div>

      {(myInvitations.data?.items.length ?? 0) > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Pending invitations for you</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {myInvitations.data?.items.map((invitation) => (
              <div
                key={invitation.id}
                className="flex flex-wrap items-center justify-between gap-3 rounded-md border p-3"
              >
                <div>
                  <p className="font-medium">{invitation.organizationName}</p>
                  <p className="text-sm text-muted-foreground">
                    Invited as {invitation.role} · expires{' '}
                    {new Date(invitation.expiresAt).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    onClick={() => acceptInvitation.mutate(invitation.id)}
                    disabled={acceptInvitation.isPending}
                  >
                    Accept
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Your memberships</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {me?.organizations.map((org) => (
            <div
              key={org.organizationId}
              className="flex items-center justify-between rounded-md border p-3"
            >
              <div className="flex items-center gap-2">
                <div>
                  <p className="font-medium">{org.organizationName}</p>
                </div>
                <RoleBadge role={org.role} />
              </div>
              {org.organizationId === organizationId && (
                <span className="text-xs font-medium text-primary">Active</span>
              )}
            </div>
          ))}
        </CardContent>
      </Card>

      {organization.isLoading && <Skeleton className="h-40 w-full" />}

      {organization.data && (
        <Card>
          <CardHeader>
            <CardTitle>Organization settings</CardTitle>
          </CardHeader>
          <CardContent>
            {canEditOrg ? (
              <form
                className="space-y-4"
                onSubmit={orgForm.handleSubmit((values) =>
                  updateOrganization.mutate(values),
                )}
              >
                <div className="space-y-2">
                  <Label htmlFor="org-name">Name</Label>
                  <Input id="org-name" {...orgForm.register('name')} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="org-slug">Slug</Label>
                  <Input id="org-slug" {...orgForm.register('slug')} />
                </div>
                {updateOrganization.isError && (
                  <p className="text-sm text-destructive">
                    {getErrorMessage(updateOrganization.error)}
                  </p>
                )}
                <Button type="submit" disabled={updateOrganization.isPending}>
                  Save changes
                </Button>
              </form>
            ) : (
              <PermissionNotice message={PERMISSION_MESSAGES.manageOrganization} />
            )}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Create organization</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            className="grid gap-4 sm:grid-cols-2"
            onSubmit={createOrgForm.handleSubmit((values) =>
              createOrganization.mutate(values, {
                onSuccess: () => createOrgForm.reset(),
              }),
            )}
          >
            <div className="space-y-2">
              <Label htmlFor="new-org-name">Name</Label>
              <Input id="new-org-name" {...createOrgForm.register('name')} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="new-org-slug">Slug</Label>
              <Input id="new-org-slug" {...createOrgForm.register('slug')} />
            </div>
            {createOrganization.isError && (
              <p className="text-sm text-destructive sm:col-span-2">
                {getErrorMessage(createOrganization.error)}
              </p>
            )}
            <Button type="submit" disabled={createOrganization.isPending}>
              Create organization
            </Button>
          </form>
        </CardContent>
      </Card>

      {organizationId && (
        <Card>
          <CardHeader>
            <CardTitle>Members</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {members.isLoading && <Skeleton className="h-24 w-full" />}
            <div className="space-y-2">
              {members.data?.items.map((member) => (
                <div
                  key={member.userId}
                  className="flex flex-wrap items-center justify-between gap-3 rounded-md border p-3"
                >
                  <div>
                    <p className="font-medium">{member.fullName ?? member.userId}</p>
                    <p className="text-sm text-muted-foreground">{member.email}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <RoleBadge role={member.role as OrganizationRole} />
                    {canManage && member.role !== 'owner' && member.userId !== me?.user.id && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => removeMember.mutate(member.userId)}
                      >
                        Remove
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {canManage ? (
              <>
                <form
                  className="grid gap-4 md:grid-cols-3"
                  onSubmit={inviteForm.handleSubmit((values) =>
                    inviteMember.mutate(values, {
                      onSuccess: () => inviteForm.reset({ role: values.role }),
                    }),
                  )}
                >
                  <div className="space-y-2 md:col-span-2">
                    <Label htmlFor="invite-email">Invite by email</Label>
                    <Input
                      id="invite-email"
                      type="email"
                      placeholder="teammate@company.com"
                      {...inviteForm.register('email')}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Role</Label>
                    <Select
                      value={inviteForm.watch('role')}
                      onValueChange={(value) =>
                        inviteForm.setValue('role', value as InviteForm['role'])
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="admin">Admin</SelectItem>
                        <SelectItem value="developer">Developer</SelectItem>
                        <SelectItem value="viewer">Viewer</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Button type="submit" disabled={inviteMember.isPending}>
                    Send invitation
                  </Button>
                </form>

                {invitations.data?.items.length ? (
                  <div className="space-y-2">
                    <p className="text-sm font-medium">Pending invitations</p>
                    {invitations.data.items.map((invitation) => (
                      <div
                        key={invitation.id}
                        className="flex items-center justify-between rounded-md border p-3"
                      >
                        <div>
                          <p className="font-medium">{invitation.email}</p>
                          <p className="text-sm text-muted-foreground">
                            {invitation.role} · expires{' '}
                            {new Date(invitation.expiresAt).toLocaleDateString()}
                          </p>
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => cancelInvitation.mutate(invitation.id)}
                        >
                          Cancel
                        </Button>
                      </div>
                    ))}
                  </div>
                ) : null}

                {canEditOrg && (
                  <div className="space-y-2 border-t pt-4">
                    <p className="text-sm font-medium">Transfer ownership</p>
                    <div className="flex flex-wrap gap-2">
                      <Select
                        value={transferUserId}
                        onValueChange={setTransferUserId}
                      >
                        <SelectTrigger className="w-64">
                          <SelectValue placeholder="Select new owner" />
                        </SelectTrigger>
                        <SelectContent>
                          {members.data?.items
                            .filter(
                              (member) =>
                                member.userId !== me?.user.id &&
                                member.role !== 'owner',
                            )
                            .map((member) => (
                              <SelectItem key={member.userId} value={member.userId}>
                                {member.fullName ?? member.email ?? member.userId}
                              </SelectItem>
                            ))}
                        </SelectContent>
                      </Select>
                      <Button
                        variant="outline"
                        disabled={!transferUserId || transferOwnership.isPending}
                        onClick={() => transferOwnership.mutate(transferUserId)}
                      >
                        Transfer ownership
                      </Button>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <PermissionNotice message={PERMISSION_MESSAGES.manageMembers} />
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
