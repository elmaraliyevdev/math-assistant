import { useMemo, useState } from 'react'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { PermissionNotice } from '@/features/organizations/components/PermissionNotice'
import { RoleBadge } from '@/features/organizations/components/RoleBadge'
import {
  useCreateOrganization,
  useOrganization,
  useOrganizationPermissions,
  useUpdateOrganization,
} from '@/features/organizations/use-organizations'
import {
  SettingsFieldGroup,
  SettingsSectionHeader,
} from '@/features/settings/components/settings-primitives'
import { canManageOrganization, PERMISSION_MESSAGES } from '@/lib/permissions'
import { getErrorMessage } from '@/services/api'
import { useOrganizationStore } from '@/stores/organization-store'
import { useMe } from '@/features/auth/use-auth'

const orgSchema = z.object({
  name: z.string().min(1),
  slug: z
    .string()
    .min(1)
    .regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, 'Use lowercase letters, numbers, and hyphens'),
  description: z.string().optional(),
})

type OrgForm = z.infer<typeof orgSchema>

export function OrganizationSection() {
  const organizationId = useOrganizationStore((state) => state.currentOrganizationId)
  const setOrganizationId = useOrganizationStore((state) => state.setCurrentOrganizationId)
  const { role } = useOrganizationPermissions()
  const organization = useOrganization(organizationId)
  const updateOrganization = useUpdateOrganization(organizationId ?? '')
  const createOrganization = useCreateOrganization()
  const { data: me } = useMe()
  const [showCreate, setShowCreate] = useState(false)

  const orgFormValues = useMemo(
    () =>
      organization.data
        ? {
            name: organization.data.name,
            slug: organization.data.slug,
            description: '',
          }
        : undefined,
    [organization.data?.name, organization.data?.slug],
  )

  const orgForm = useForm<OrgForm>({
    resolver: zodResolver(orgSchema),
    values: orgFormValues,
  })

  const createOrgForm = useForm<OrgForm>({
    resolver: zodResolver(orgSchema),
    defaultValues: { name: '', slug: '', description: '' },
  })

  const canEditOrg = canManageOrganization(role)

  return (
    <div className="space-y-5">
      <SettingsSectionHeader
        title="Organization"
        description="Workspace identity and defaults for your team."
        aiPrompt="Recommend workspace settings for a game math studio"
      />

      {me?.organizations.length ? (
        <SettingsFieldGroup title="Your workspaces">
          <div className="divide-y rounded-md border">
            {me.organizations.map((org) => (
              <button
                key={org.organizationId}
                type="button"
                onClick={() => setOrganizationId(org.organizationId)}
                className="flex w-full items-center justify-between gap-3 px-3 py-2.5 text-left hover:bg-muted/40"
              >
                <div>
                  <p className="text-sm font-medium">{org.organizationName}</p>
                  <p className="text-xs text-muted-foreground">{org.organizationId}</p>
                </div>
                <div className="flex items-center gap-2">
                  <RoleBadge role={org.role} />
                  {org.organizationId === organizationId ? (
                    <span className="text-xs font-medium text-primary">Active</span>
                  ) : null}
                </div>
              </button>
            ))}
          </div>
        </SettingsFieldGroup>
      ) : null}

      {organization.isLoading && <Skeleton className="h-40 w-full" />}

      {organization.data ? (
        <SettingsFieldGroup title="Workspace details">
          {canEditOrg ? (
            <form
              className="grid max-w-xl gap-3"
              onSubmit={orgForm.handleSubmit((values) =>
                updateOrganization.mutate({
                  name: values.name,
                  slug: values.slug,
                }),
              )}
            >
              <div className="space-y-1.5">
                <Label htmlFor="org-name">Workspace name</Label>
                <Input id="org-name" {...orgForm.register('name')} />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="org-slug">Workspace slug</Label>
                <Input id="org-slug" {...orgForm.register('slug')} />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="org-description">Description</Label>
                <Input
                  id="org-description"
                  placeholder="What does this workspace build?"
                  {...orgForm.register('description')}
                  disabled
                />
                <p className="text-xs text-muted-foreground">Coming soon.</p>
              </div>
              <div className="space-y-1.5">
                <Label>Workspace logo</Label>
                <Input placeholder="Logo upload coming soon" disabled />
              </div>
              <div className="space-y-1.5">
                <Label>Organization visibility</Label>
                <Input value="Private to members" disabled />
              </div>
              {updateOrganization.isError ? (
                <p className="text-sm text-destructive">
                  {getErrorMessage(updateOrganization.error)}
                </p>
              ) : null}
              <Button type="submit" size="sm" className="w-fit" disabled={updateOrganization.isPending}>
                Save changes
              </Button>
            </form>
          ) : (
            <PermissionNotice message={PERMISSION_MESSAGES.manageOrganization} />
          )}
        </SettingsFieldGroup>
      ) : null}

      <SettingsFieldGroup title="Create workspace">
        {showCreate ? (
          <form
            className="grid max-w-xl gap-3"
            onSubmit={createOrgForm.handleSubmit((values) =>
              createOrganization.mutate(
                { name: values.name, slug: values.slug },
                {
                  onSuccess: () => {
                    createOrgForm.reset()
                    setShowCreate(false)
                  },
                },
              ),
            )}
          >
            <div className="space-y-1.5">
              <Label htmlFor="new-org-name">Name</Label>
              <Input id="new-org-name" {...createOrgForm.register('name')} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="new-org-slug">Slug</Label>
              <Input id="new-org-slug" {...createOrgForm.register('slug')} />
            </div>
            {createOrganization.isError ? (
              <p className="text-sm text-destructive">
                {getErrorMessage(createOrganization.error)}
              </p>
            ) : null}
            <div className="flex gap-2">
              <Button type="submit" size="sm" disabled={createOrganization.isPending}>
                Create workspace
              </Button>
              <Button type="button" variant="outline" size="sm" onClick={() => setShowCreate(false)}>
                Cancel
              </Button>
            </div>
          </form>
        ) : (
          <Button variant="outline" size="sm" onClick={() => setShowCreate(true)}>
            New workspace
          </Button>
        )}
      </SettingsFieldGroup>
    </div>
  )
}
