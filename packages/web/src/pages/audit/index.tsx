import { redirect } from '@tanstack/react-router'

export function AuditPageRedirect() {
  throw redirect({ to: '/settings', search: { section: 'audit' } })
}
