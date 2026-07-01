import { useState } from 'react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  SettingsFieldGroup,
  SettingsSectionHeader,
} from '@/features/settings/components/settings-primitives'
import { useChangePassword } from '@/features/settings/hooks/use-settings'

export function SecuritySection() {
  const changePassword = useChangePassword()
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')

  return (
    <div className="space-y-5">
      <SettingsSectionHeader
        title="Security"
        description="Password, sessions, and account protection."
        aiPrompt="What security settings should I enable for my workspace?"
      />

      <SettingsFieldGroup title="Password">
        <div className="grid max-w-md gap-3">
          <div className="space-y-1.5">
            <Label htmlFor="currentPassword">Current password</Label>
            <Input
              id="currentPassword"
              type="password"
              value={currentPassword}
              onChange={(event) => setCurrentPassword(event.target.value)}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="newPassword">New password</Label>
            <Input
              id="newPassword"
              type="password"
              value={newPassword}
              onChange={(event) => setNewPassword(event.target.value)}
            />
          </div>
          <Button
            size="sm"
            className="w-fit"
            onClick={() =>
              changePassword.mutate(
                { currentPassword, newPassword },
                {
                  onSuccess: () => {
                    setCurrentPassword('')
                    setNewPassword('')
                  },
                },
              )
            }
            disabled={changePassword.isPending}
          >
            Change password
          </Button>
        </div>
      </SettingsFieldGroup>

      <SettingsFieldGroup title="Sessions" description="Manage active sign-ins.">
        <p className="text-sm text-muted-foreground">Session management coming soon.</p>
      </SettingsFieldGroup>

      <SettingsFieldGroup title="Multi-factor authentication">
        <p className="text-sm text-muted-foreground">MFA setup coming soon.</p>
      </SettingsFieldGroup>

      <SettingsFieldGroup title="API tokens">
        <p className="text-sm text-muted-foreground">
          Personal API tokens will be available in a future release.
        </p>
      </SettingsFieldGroup>
    </div>
  )
}
