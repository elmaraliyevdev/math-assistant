import type { ReactNode } from 'react'

import { SectionHeader } from '@/components/design-system/page-layout'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import {
  PROJECT_STATUS_STYLES,
  type ProjectStatus,
} from '@/features/workspace/lib/workspace-status'
import { cn } from '@/lib/utils'

export function WorkspacePanel({
  title,
  description,
  action,
  children,
  className,
}: {
  title?: ReactNode
  description?: string
  action?: ReactNode
  children: ReactNode
  className?: string
}) {
  return (
    <Card className={cn('shadow-none', className)}>
      {(title || action) && (
        <CardHeader className="pb-4">
          {typeof title === 'string' ? (
            <SectionHeader title={title} description={description} action={action} />
          ) : (
            <div className="flex items-center justify-between gap-3">
              {title}
              {action}
            </div>
          )}
        </CardHeader>
      )}
      <CardContent className={cn(!title && !action && 'pt-6')}>{children}</CardContent>
    </Card>
  )
}

export function ProjectStatusBadge({
  label,
  status,
}: {
  label: string
  status: ProjectStatus
}) {
  return (
    <span
      className={cn(
        'inline-flex shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium',
        PROJECT_STATUS_STYLES[status],
      )}
    >
      {label}
    </span>
  )
}
