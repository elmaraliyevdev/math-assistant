import { useState } from 'react'

import { Avatar, AvatarFallback, getInitials } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ConfirmDialog } from '@/components/ui/confirm-dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { EmptyState } from '@/components/design-system'
import { useMe } from '@/features/auth/use-auth'
import { PermissionNotice } from '@/features/organizations/components/PermissionNotice'
import { RoleBadge } from '@/features/organizations/components/RoleBadge'
import {
  InviteMemberDialog,
  type InviteForm,
} from '@/features/settings/components/InviteMemberDialog'
import { getRoleLabel } from '@/features/settings/components/RoleSelect'
import {
  SettingsDangerZone,
  SettingsFieldGroup,
  SettingsSectionHeader,
} from '@/features/settings/components/settings-primitives'
import {
  useAcceptInvitation,
  useCancelInvitation,
  useInviteMember,
  useMyInvitations,
  useOrganizationInvitations,
} from '@/features/organizations/use-invitations'
import {
  useOrganizationMembers,
  useOrganizationPermissions,
  useRemoveOrganizationMember,
  useTransferOwnership,
} from '@/features/organizations/use-organizations'
import { canManageMembers, canManageOrganization, PERMISSION_MESSAGES } from '@/lib/permissions'
import { formatDate } from '@/lib/utils'
import { useOrganizationStore } from '@/stores/organization-store'
import type { OrganizationRole } from '@/types/api'

export function TeamSection() {
  const organizationId = useOrganizationStore((state) => state.currentOrganizationId)
  const { role } = useOrganizationPermissions()
  const members = useOrganizationMembers(organizationId)
  const invitations = useOrganizationInvitations(organizationId)
  const myInvitations = useMyInvitations()
  const { data: me } = useMe()
  const inviteMember = useInviteMember(organizationId ?? '')
  const cancelInvitation = useCancelInvitation(organizationId ?? '')
  const removeMember = useRemoveOrganizationMember(organizationId ?? '')
  const transferOwnership = useTransferOwnership(organizationId ?? '')
  const acceptInvitation = useAcceptInvitation()

  const [inviteOpen, setInviteOpen] = useState(false)
  const [transferUserId, setTransferUserId] = useState('')
  const [transferOpen, setTransferOpen] = useState(false)

  const canManage = canManageMembers(role)
  const canEditOrg = canManageOrganization(role)

  const handleInvite = (values: InviteForm) => {
    inviteMember.mutate(values, {
      onSuccess: () => setInviteOpen(false),
    })
  }

  const handleResend = (email: string, role: OrganizationRole) => {
    if (role === 'owner') return
    inviteMember.mutate({ email, role })
  }

  if (!organizationId) {
    return (
      <div className="space-y-4">
        <SettingsSectionHeader
          title="Team"
          description="Invite teammates and manage workspace roles."
        />
        <EmptyState
          title="No workspace selected"
          description="Create or select a workspace in Organization settings to manage your team."
        />
      </div>
    )
  }

  return (
    <div className="space-y-5">
      <SettingsSectionHeader
        title="Team"
        description="Manage members, roles, and pending invitations."
        aiPrompt="How should I structure roles for a slot math team?"
        actions={
          canManage ? (
            <Button size="sm" onClick={() => setInviteOpen(true)}>
              Invite member
            </Button>
          ) : null
        }
      />

      {(myInvitations.data?.items.length ?? 0) > 0 ? (
        <SettingsFieldGroup title="Invitations for you">
          <div className="divide-y rounded-md border">
            {myInvitations.data?.items.map((invitation) => (
              <div
                key={invitation.id}
                className="flex flex-wrap items-center justify-between gap-3 px-3 py-2.5"
              >
                <div>
                  <p className="text-sm font-medium">{invitation.organizationName}</p>
                  <p className="text-xs text-muted-foreground">
                    Invited as {getRoleLabel(invitation.role)} · expires{' '}
                    {new Date(invitation.expiresAt).toLocaleDateString()}
                  </p>
                </div>
                <Button
                  size="sm"
                  onClick={() => acceptInvitation.mutate(invitation.id)}
                  disabled={acceptInvitation.isPending}
                >
                  Accept
                </Button>
              </div>
            ))}
          </div>
        </SettingsFieldGroup>
      ) : null}

      <SettingsFieldGroup title="Team members">
        {members.isLoading ? <Skeleton className="h-32 w-full" /> : null}
        {(members.data?.items.length ?? 0) === 0 && !members.isLoading ? (
          <EmptyState
            title="Invite your first teammate"
            description="Collaborate on games, simulations, and certification in this workspace."
            action={
              canManage ? (
                <Button size="sm" onClick={() => setInviteOpen(true)}>
                  Invite member
                </Button>
              ) : undefined
            }
          />
        ) : (
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Member</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {members.data?.items.map((member) => {
                  const name = member.fullName ?? member.email ?? member.userId
                  return (
                    <TableRow key={member.userId}>
                      <TableCell>
                        <div className="flex items-center gap-2.5">
                          <Avatar className="h-8 w-8">
                            <AvatarFallback className="text-xs">
                              {getInitials(name)}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <p className="text-sm font-medium">{name}</p>
                            <p className="text-xs text-muted-foreground">{member.email}</p>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <RoleBadge role={member.role as OrganizationRole} />
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className="font-normal">
                          Active
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        {canManage &&
                        member.role !== 'owner' &&
                        member.userId !== me?.user.id ? (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => removeMember.mutate(member.userId)}
                          >
                            Remove
                          </Button>
                        ) : (
                          <span className="text-xs text-muted-foreground">—</span>
                        )}
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </div>
        )}
      </SettingsFieldGroup>

      {!canManage ? (
        <PermissionNotice message={PERMISSION_MESSAGES.manageMembers} />
      ) : null}

      {(invitations.data?.items.length ?? 0) > 0 ? (
        <SettingsFieldGroup title="Pending invitations">
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Email</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Invited</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {invitations.data?.items.map((invitation) => (
                  <TableRow key={invitation.id}>
                    <TableCell className="text-sm">{invitation.email}</TableCell>
                    <TableCell>
                      <RoleBadge role={invitation.role} />
                    </TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {formatDate(invitation.createdAt)}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() =>
                            handleResend(
                              invitation.email,
                              invitation.role as OrganizationRole,
                            )
                          }
                          disabled={inviteMember.isPending}
                        >
                          Resend
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => cancelInvitation.mutate(invitation.id)}
                        >
                          Cancel
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </SettingsFieldGroup>
      ) : null}

      {canEditOrg ? (
        <SettingsDangerZone
          title="Danger zone"
          description="Sensitive workspace actions."
        >
          <div className="space-y-3">
            <p className="text-sm font-medium">Transfer workspace ownership</p>
            <p className="text-xs text-muted-foreground">
              Assign full control of this workspace to another active member.
            </p>
            <Select value={transferUserId} onValueChange={setTransferUserId}>
              <SelectTrigger className="max-w-sm">
                <SelectValue placeholder="Select new owner" />
              </SelectTrigger>
              <SelectContent>
                {members.data?.items
                  .filter(
                    (member) =>
                      member.userId !== me?.user.id && member.role !== 'owner',
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
              size="sm"
              disabled={!transferUserId}
              onClick={() => setTransferOpen(true)}
            >
              Transfer ownership
            </Button>
          </div>
        </SettingsDangerZone>
      ) : null}

      <InviteMemberDialog
        open={inviteOpen}
        onOpenChange={setInviteOpen}
        onInvite={handleInvite}
        isPending={inviteMember.isPending}
        error={inviteMember.error}
      />

      <ConfirmDialog
        open={transferOpen}
        onOpenChange={setTransferOpen}
        title="Transfer workspace ownership"
        description="You will lose owner privileges. This action cannot be undone without the new owner transferring back."
        confirmLabel="Transfer ownership"
        destructive
        loading={transferOwnership.isPending}
        onConfirm={() => {
          if (!transferUserId) return
          transferOwnership.mutate(transferUserId, {
            onSuccess: () => {
              setTransferOpen(false)
              setTransferUserId('')
            },
          })
        }}
      />
    </div>
  )
}