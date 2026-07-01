const SEGMENT_LABELS: Record<string, string> = {
  dashboard: 'Workspace',
  games: 'Games',
  create: 'Create',
  versions: 'Versions',
  'reel-studio': 'Studio',
  templates: 'Templates',
  simulations: 'Simulations',
  compare: 'Compare',
  review: 'Review',
  mathematics: 'Mathematics',
  assistant: 'AI Assistant',
  organizations: 'Organization',
  settings: 'Settings',
  audit: 'Audit log',
  demo: 'Demo',
  admin: 'Admin',
  contact: 'Contact',
  onboarding: 'Onboarding',
}

const HIDDEN_SEGMENTS = new Set(['versions'])

export interface BreadcrumbItem {
  label: string
  path?: string
}

export function buildBreadcrumbs(pathname: string): BreadcrumbItem[] {
  if (pathname === '/dashboard' || pathname === '/') {
    return [{ label: 'Workspace' }]
  }

  const segments = pathname.split('/').filter(Boolean)
  if (segments.length === 0) {
    return []
  }

  const items: BreadcrumbItem[] = []
  let path = ''

  for (let index = 0; index < segments.length; index += 1) {
    const segment = segments[index]
    path += `/${segment}`

    if (HIDDEN_SEGMENTS.has(segment)) {
      continue
    }

    const isDynamic =
      segment.includes('-') && segment.length > 20
        ? true
        : /^[0-9a-f-]{8,}$/i.test(segment) || /^\d+$/.test(segment)

    if (isDynamic) {
      if (segments[index - 1] === 'games' && segments[index + 1] === undefined) {
        return items
      }
      if (segments[index - 1] === 'games') {
        items.push({ label: 'Game' })
      } else if (segments[index - 1] === 'simulations') {
        items.push({ label: 'Simulation' })
      } else if (segment === segments[segments.length - 1] && segments.includes('reel-studio')) {
        items.push({ label: 'Design Studio' })
      } else {
        items.push({ label: 'Details' })
      }
      continue
    }

    const label = SEGMENT_LABELS[segment] ?? segment.replace(/-/g, ' ')
    const isLast = index === segments.length - 1
    items.push({
      label: label.charAt(0).toUpperCase() + label.slice(1),
      path: isLast ? undefined : path,
    })
  }

  return items
}
