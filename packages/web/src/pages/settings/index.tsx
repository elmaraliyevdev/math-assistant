import { useEffect, useState } from 'react'

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
import {
  useChangePassword,
  useUpdatePreferences,
  useUpdateProfile,
  useUserPreferences,
} from '@/features/settings/hooks/use-settings'
import { useThemeStore } from '@/stores/theme-store'

export function SettingsPage() {
  const me = useMe()
  const preferences = useUserPreferences()
  const updatePreferences = useUpdatePreferences()
  const updateProfile = useUpdateProfile()
  const changePassword = useChangePassword()
  const theme = useThemeStore((state) => state.theme)

  const [fullName, setFullName] = useState('')
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')

  useEffect(() => {
    if (me.data?.user.fullName) {
      setFullName(me.data.user.fullName)
    }
  }, [me.data?.user.fullName])

  if (preferences.isLoading || me.isLoading) {
    return <Skeleton className="h-64 w-full" />
  }

  const prefs = preferences.data

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Settings</h2>
        <p className="text-muted-foreground">
          Manage your profile, security, and preferences.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Profile</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" value={me.data?.user.email ?? ''} disabled />
          </div>
          <div className="space-y-2">
            <Label htmlFor="fullName">Full name</Label>
            <Input
              id="fullName"
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
            />
          </div>
          <Button
            onClick={() => updateProfile.mutate({ fullName })}
            disabled={updateProfile.isPending}
          >
            Save profile
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Password</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="currentPassword">Current password</Label>
            <Input
              id="currentPassword"
              type="password"
              value={currentPassword}
              onChange={(event) => setCurrentPassword(event.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="newPassword">New password</Label>
            <Input
              id="newPassword"
              type="password"
              value={newPassword}
              onChange={(event) => setNewPassword(event.target.value)}
            />
          </div>
          <Button
            onClick={() =>
              changePassword.mutate({ currentPassword, newPassword })
            }
            disabled={changePassword.isPending}
          >
            Change password
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Appearance</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Theme</Label>
            <Select
              value={theme}
              onValueChange={(value) =>
                updatePreferences.mutate({
                  theme: value,
                })
              }
            >
              <SelectTrigger className="w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="light">Light</SelectItem>
                <SelectItem value="dark">Dark</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Notifications</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {prefs && (
            <>
              <PreferenceToggle
                label="Simulation completed"
                checked={prefs.notifySimulationCompleted}
                onChange={(checked) =>
                  updatePreferences.mutate({
                    notifySimulationCompleted: checked,
                  })
                }
              />
              <PreferenceToggle
                label="Simulation failed"
                checked={prefs.notifySimulationFailed}
                onChange={(checked) =>
                  updatePreferences.mutate({ notifySimulationFailed: checked })
                }
              />
              <PreferenceToggle
                label="Validation failures"
                checked={prefs.notifyValidationFailed}
                onChange={(checked) =>
                  updatePreferences.mutate({
                    notifyValidationFailed: checked,
                  })
                }
              />
              <PreferenceToggle
                label="Organization invitations"
                checked={prefs.notifyOrganizationInvitation}
                onChange={(checked) =>
                  updatePreferences.mutate({
                    notifyOrganizationInvitation: checked,
                  })
                }
              />
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function PreferenceToggle({
  label,
  checked,
  onChange,
}: {
  label: string
  checked: boolean
  onChange: (checked: boolean) => void
}) {
  return (
    <label className="flex items-center justify-between gap-4 text-sm">
      <span>{label}</span>
      <input
        type="checkbox"
        checked={checked}
        onChange={(event) => onChange(event.target.checked)}
        className="h-4 w-4"
      />
    </label>
  )
}
