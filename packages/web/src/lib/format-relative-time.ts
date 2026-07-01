export function formatRelativeTime(value: string | null | undefined): string {
  if (!value) return '—'
  const date = new Date(value)
  const diffMs = date.getTime() - Date.now()
  const absSeconds = Math.round(Math.abs(diffMs) / 1000)
  const rtf = new Intl.RelativeTimeFormat(undefined, { numeric: 'auto' })

  if (absSeconds < 60) return rtf.format(Math.round(diffMs / 1000), 'second')
  if (absSeconds < 3600) return rtf.format(Math.round(diffMs / 60_000), 'minute')
  if (absSeconds < 86_400) return rtf.format(Math.round(diffMs / 3_600_000), 'hour')
  if (absSeconds < 86_400 * 7) return rtf.format(Math.round(diffMs / 86_400_000), 'day')
  return rtf.format(Math.round(diffMs / (86_400_000 * 30)), 'month')
}

export function workspaceGreeting(name: string): string {
  const hour = new Date().getHours()
  const first = name.trim().split(/\s+/)[0] || name
  if (hour < 12) return `Good morning, ${first}`
  if (hour < 18) return `Good afternoon, ${first}`
  return `Good evening, ${first}`
}
