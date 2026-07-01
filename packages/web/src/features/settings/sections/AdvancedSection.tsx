import { Link } from '@tanstack/react-router'

import { Button } from '@/components/ui/button'
import {
  SettingsFieldGroup,
  SettingsSectionHeader,
} from '@/features/settings/components/settings-primitives'

export function AdvancedSection() {
  return (
    <div className="space-y-5">
      <SettingsSectionHeader
        title="Advanced"
        description="Developer tools, integrations, and workspace utilities."
      />

      <SettingsFieldGroup title="Workspace tools">
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" size="sm" asChild>
            <Link to="/templates">Templates</Link>
          </Button>
          <Button variant="outline" size="sm" asChild>
            <Link to="/mathematics">Mathematics workbench</Link>
          </Button>
          <Button variant="outline" size="sm" asChild>
            <Link to="/demo">Demo mode</Link>
          </Button>
        </div>
      </SettingsFieldGroup>

      <SettingsFieldGroup title="API keys">
        <p className="text-sm text-muted-foreground">Workspace API keys coming soon.</p>
      </SettingsFieldGroup>

      <SettingsFieldGroup title="Integrations">
        <p className="text-sm text-muted-foreground">
          Connect CI, Slack, and Jira from this section in a future release.
        </p>
      </SettingsFieldGroup>

      <SettingsFieldGroup title="Billing & usage">
        <p className="text-sm text-muted-foreground">
          Usage meters and billing controls will appear here.
        </p>
      </SettingsFieldGroup>
    </div>
  )
}
