import { useEffect, useState } from 'react'

import { Avatar, AvatarFallback, getInitials } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { useMe } from '@/features/auth/use-auth'
import {
  SettingsDangerZone,
  SettingsFieldGroup,
  SettingsSectionHeader,
} from '@/features/settings/components/settings-primitives'
import { useUpdateProfile } from '@/features/settings/hooks/use-settings'

export function ProfileSection() {
  const me = useMe()
  const updateProfile = useUpdateProfile()
  const [fullName, setFullName] = useState('')

  useEffect(() => {
    if (me.data?.user.fullName) {
      setFullName(me.data.user.fullName)
    }
  }, [me.data?.user.fullName])

  if (me.isLoading) {
    return <Skeleton className="h-48 w-full" />
  }

  const user = me.data?.user
  const displayName = user?.fullName ?? user?.email ?? 'User'

  return (
    <div className="space-y-5">
      <SettingsSectionHeader
        title="Profile"
        description="Your personal account details and preferences."
        aiPrompt="Recommend profile settings for a slot game math team"
      />

      <SettingsFieldGroup title="Avatar">
        <div className="flex items-center gap-3">
          <Avatar className="h-14 w-14">
            <AvatarFallback className="text-base">{getInitials(displayName)}</AvatarFallback>
          </Avatar>
          <p className="text-sm text-muted-foreground">
            Avatar uploads coming soon.
          </p>
        </div>
      </SettingsFieldGroup>

      <SettingsFieldGroup title="Name">
        <div className="grid max-w-md gap-3">
          <div className="space-y-1.5">
            <Label htmlFor="fullName">Full name</Label>
            <Input
              id="fullName"
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
            />
          </div>
          <Button
            size="sm"
            className="w-fit"
            onClick={() => updateProfile.mutate({ fullName })}
            disabled={updateProfile.isPending}
          >
            Save profile
          </Button>
        </div>
      </SettingsFieldGroup>

      <SettingsFieldGroup title="Email">
        <Input className="max-w-md" value={user?.email ?? ''} disabled />
      </SettingsFieldGroup>

      <SettingsFieldGroup title="Timezone" description="Used for reports and notifications.">
        <Input className="max-w-md" value="Auto-detect (browser)" disabled />
      </SettingsFieldGroup>

      <SettingsFieldGroup title="Language">
        <Input className="max-w-md" value="English" disabled />
      </SettingsFieldGroup>

      <SettingsDangerZone
        title="Danger zone"
        description="Irreversible account actions."
      >
        <Button variant="outline" size="sm" disabled>
          Delete account (coming soon)
        </Button>
      </SettingsDangerZone>
    </div>
  )
}
