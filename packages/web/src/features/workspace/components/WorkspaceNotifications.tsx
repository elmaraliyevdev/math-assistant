import { Link } from '@tanstack/react-router'
import { ArrowRight, Bell, CheckCircle2, FlaskConical, Users } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { WorkspacePanel } from '@/features/workspace/components/WorkspacePanel'
import type { Notification } from '@/services/notifications'
import { formatRelativeTime } from '@/lib/format-relative-time'
import { cn } from '@/lib/utils'

function notificationIcon(type: string) {
  if (type.includes('simulation')) return FlaskConical
  if (type.includes('invitation') || type.includes('review')) return Users
  if (type.includes('validation')) return CheckCircle2
  return Bell
}

export function WorkspaceNotifications({
  loading,
  notifications,
}: {
  loading: boolean
  notifications: Notification[]
}) {
  if (loading) {
    return (
      <WorkspacePanel title="Notifications">
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, index) => (
            <Skeleton key={index} className="h-10 w-full" />
          ))}
        </div>
      </WorkspacePanel>
    )
  }

  if (!notifications.length) {
    return null
  }

  return (
    <WorkspacePanel
      title="Notifications"
      action={
        <Button variant="ghost" size="sm" className="h-8 gap-1 text-xs" asChild>
          <Link to="/settings">
            View all
            <ArrowRight className="h-3 w-3" />
          </Link>
        </Button>
      }
    >
      <ul className="space-y-1">
        {notifications.map((item) => {
          const Icon = notificationIcon(item.type)
          return (
            <li key={item.id}>
              <div
                className={cn(
                  'flex items-start gap-3 rounded-lg px-2 py-2 transition-colors hover:bg-muted/30',
                  !item.readAt && 'bg-muted/20',
                )}
              >
                <Icon className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium">{item.title}</p>
                  <p className="text-xs text-muted-foreground">
                    {formatRelativeTime(item.createdAt)}
                  </p>
                </div>
                {!item.readAt ? (
                  <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-primary" />
                ) : null}
              </div>
            </li>
          )
        })}
      </ul>
    </WorkspacePanel>
  )
}
