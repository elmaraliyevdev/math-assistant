import { Badge } from '@/components/ui/badge'
import type { OrganizationRole } from '@/types/api'
import { cn } from '@/lib/utils'

const ROLE_STYLES: Record<OrganizationRole, string> = {
  owner: 'bg-amber-100 text-amber-900 dark:bg-amber-950 dark:text-amber-100',
  admin: 'bg-blue-100 text-blue-900 dark:bg-blue-950 dark:text-blue-100',
  developer: 'bg-emerald-100 text-emerald-900 dark:bg-emerald-950 dark:text-emerald-100',
  viewer: 'bg-muted text-muted-foreground',
}

interface RoleBadgeProps {
  role: OrganizationRole
  className?: string
}

export function RoleBadge({ role, className }: RoleBadgeProps) {
  return (
    <Badge variant="outline" className={cn('capitalize', ROLE_STYLES[role], className)}>
      {role}
    </Badge>
  )
}
