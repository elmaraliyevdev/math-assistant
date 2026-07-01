export const SETTINGS_SECTIONS = [
  { id: 'profile', label: 'Profile' },
  { id: 'organization', label: 'Organization' },
  { id: 'team', label: 'Team' },
  { id: 'security', label: 'Security' },
  { id: 'notifications', label: 'Notifications' },
  { id: 'audit', label: 'Audit log' },
  { id: 'appearance', label: 'Appearance' },
  { id: 'advanced', label: 'Advanced' },
] as const

export type SettingsSectionId = (typeof SETTINGS_SECTIONS)[number]['id']

export const DEFAULT_SETTINGS_SECTION: SettingsSectionId = 'profile'

export function isSettingsSection(value: string | undefined): value is SettingsSectionId {
  return SETTINGS_SECTIONS.some((section) => section.id === value)
}

export function resolveSettingsSection(value: string | undefined): SettingsSectionId {
  return isSettingsSection(value) ? value : DEFAULT_SETTINGS_SECTION
}
