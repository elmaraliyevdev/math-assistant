import { Skeleton } from '@/components/ui/skeleton'
import {
  SettingSwitchRow,
  SettingsFieldGroup,
  SettingsSectionHeader,
} from '@/features/settings/components/settings-primitives'
import {
  useUpdatePreferences,
  useUserPreferences,
} from '@/features/settings/hooks/use-settings'

export function NotificationsSection() {
  const preferences = useUserPreferences()
  const updatePreferences = useUpdatePreferences()

  if (preferences.isLoading) {
    return <Skeleton className="h-48 w-full" />
  }

  const prefs = preferences.data
  if (!prefs) return null

  return (
    <div className="space-y-5">
      <SettingsSectionHeader
        title="Notifications"
        description="Choose what we email you about."
        aiPrompt="Which notifications should a game math lead enable?"
      />

      <SettingsFieldGroup title="Email notifications">
        <div className="space-y-2">
          <SettingSwitchRow
            label="Simulation completed"
            description="When a long-running simulation finishes successfully."
            checked={prefs.notifySimulationCompleted}
            onCheckedChange={(checked) =>
              updatePreferences.mutate({ notifySimulationCompleted: checked })
            }
          />
          <SettingSwitchRow
            label="Simulation failed"
            description="When a simulation stops with errors or validation issues."
            checked={prefs.notifySimulationFailed}
            onCheckedChange={(checked) =>
              updatePreferences.mutate({ notifySimulationFailed: checked })
            }
          />
          <SettingSwitchRow
            label="Certification completed"
            description="When a certification report is generated."
            checked={prefs.notifySimulationCompleted}
            onCheckedChange={() => undefined}
            disabled
          />
          <SettingSwitchRow
            label="Validation failed"
            description="When canonical JSON or math validation fails."
            checked={prefs.notifyValidationFailed}
            onCheckedChange={(checked) =>
              updatePreferences.mutate({ notifyValidationFailed: checked })
            }
          />
          <SettingSwitchRow
            label="Invitations"
            description="When you are invited to a workspace."
            checked={prefs.notifyOrganizationInvitation}
            onCheckedChange={(checked) =>
              updatePreferences.mutate({ notifyOrganizationInvitation: checked })
            }
          />
          <SettingSwitchRow
            label="Product updates"
            description="Occasional news about features and improvements."
            checked={false}
            onCheckedChange={() => undefined}
            disabled
          />
          <SettingSwitchRow
            label="Security alerts"
            description="Sign-in attempts and password changes."
            checked={false}
            onCheckedChange={() => undefined}
            disabled
          />
        </div>
      </SettingsFieldGroup>
    </div>
  )
}
