import { useSearch } from '@tanstack/react-router'

import { SettingsLayout } from '@/features/settings/components/SettingsLayout'
import { AdvancedSection } from '@/features/settings/sections/AdvancedSection'
import { AppearanceSection } from '@/features/settings/sections/AppearanceSection'
import { AuditSection } from '@/features/settings/sections/AuditSection'
import { NotificationsSection } from '@/features/settings/sections/NotificationsSection'
import { OrganizationSection } from '@/features/settings/sections/OrganizationSection'
import { ProfileSection } from '@/features/settings/sections/ProfileSection'
import { SecuritySection } from '@/features/settings/sections/SecuritySection'
import { TeamSection } from '@/features/settings/sections/TeamSection'
import { resolveSettingsSection } from '@/features/settings/settings-sections'

export function SettingsPage() {
  const search = useSearch({ strict: false }) as { section?: string }
  const section = resolveSettingsSection(search.section)

  return (
    <SettingsLayout section={section}>
      {section === 'profile' ? <ProfileSection /> : null}
      {section === 'organization' ? <OrganizationSection /> : null}
      {section === 'team' ? <TeamSection /> : null}
      {section === 'security' ? <SecuritySection /> : null}
      {section === 'notifications' ? <NotificationsSection /> : null}
      {section === 'audit' ? <AuditSection /> : null}
      {section === 'appearance' ? <AppearanceSection /> : null}
      {section === 'advanced' ? <AdvancedSection /> : null}
    </SettingsLayout>
  )
}
