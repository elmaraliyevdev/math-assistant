import { redirect } from '@tanstack/react-router'

export function OrganizationSettingsRedirect() {
  throw redirect({ to: '/settings', search: { section: 'team' } })
}
