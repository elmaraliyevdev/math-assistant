import { Bell } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { useNavigate } from '@tanstack/react-router'

import { Badge, statusBadgeVariant } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  isReviewNotification,
  reviewNotificationHref,
} from '@/features/collaboration/review-workflow'
import {
  useMarkAllNotificationsRead,
  useMarkNotificationRead,
  useNotifications,
} from '@/features/notifications/hooks/use-notifications'
import { formatDate, cn } from '@/lib/utils'

export function NotificationCenter({
  variant = 'icon',
  className,
}: {
  variant?: 'icon' | 'sidebar'
  className?: string
}) {
  const navigate = useNavigate()
  const [type, setType] = useState('all')
  const notifications = useNotifications({
    page: 1,
    pageSize: 20,
    type: type === 'all' ? undefined : type,
  })
  const markRead = useMarkNotificationRead()
  const markAllRead = useMarkAllNotificationsRead()
  const [open, setOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const unreadCount = notifications.data?.unreadCount ?? 0

  useEffect(() => {
    if (!open) return
    const handlePointerDown = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handlePointerDown)
    return () => document.removeEventListener('mousedown', handlePointerDown)
  }, [open])

  const panel = open ? (
    <div
      className={cn(
        'z-50 rounded-lg border bg-card p-4 shadow-lg',
        variant === 'sidebar'
          ? 'absolute bottom-0 left-full mb-0 ml-2 w-96'
          : 'absolute right-0 mt-2 w-96',
      )}
    >
      <div className="mb-3 flex items-center justify-between gap-2">
        <h3 className="font-semibold">Notifications</h3>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => markAllRead.mutate()}
          disabled={markAllRead.isPending}
        >
          Mark all read
        </Button>
      </div>
      <Select value={type} onValueChange={setType}>
        <SelectTrigger className="mb-3">
          <SelectValue placeholder="Filter by type" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All types</SelectItem>
          <SelectItem value="simulation_completed">Completed</SelectItem>
          <SelectItem value="simulation_failed">Failed</SelectItem>
          <SelectItem value="validation_failed">Validation</SelectItem>
          <SelectItem value="organization_invitation">Invitations</SelectItem>
          <SelectItem value="review_requested">Review requested</SelectItem>
          <SelectItem value="changes_requested">Changes requested</SelectItem>
          <SelectItem value="simulation_approved">Simulation approved</SelectItem>
          <SelectItem value="certification_ready">Certification ready</SelectItem>
        </SelectContent>
      </Select>
      <div className="max-h-80 space-y-2 overflow-y-auto">
        {notifications.data?.items.map((item) => {
          const reviewHref = reviewNotificationHref(item.entityType, item.entityId)
          const isActionableReview = isReviewNotification(item.type) && reviewHref
          return (
            <button
              key={item.id}
              type="button"
              className={cn(
                'w-full rounded-md border p-3 text-left text-sm transition-colors hover:bg-accent',
                item.readAt
                  ? 'opacity-70'
                  : isActionableReview
                    ? 'border-amber-500/40 bg-amber-500/5'
                    : 'border-primary/30',
              )}
              onClick={() => {
                if (!item.readAt) markRead.mutate(item.id)
                if (reviewHref) {
                  navigate({ to: reviewHref })
                  setOpen(false)
                }
              }}
            >
              <div className="flex items-center justify-between gap-2">
                <p className="font-medium">{item.title}</p>
                {isActionableReview && !item.readAt && (
                  <Badge variant={statusBadgeVariant('running')}>Action needed</Badge>
                )}
              </div>
              <p className="text-muted-foreground">{item.message}</p>
              <p className="mt-1 text-xs text-muted-foreground">{formatDate(item.createdAt)}</p>
            </button>
          )
        })}
        {!notifications.isLoading && (notifications.data?.items.length ?? 0) === 0 && (
          <p className="text-sm text-muted-foreground">No notifications.</p>
        )}
      </div>
    </div>
  ) : null

  if (variant === 'sidebar') {
    return (
      <div ref={containerRef} className={cn('relative', className)}>
        <Button
          variant="ghost"
          className="h-9 w-full justify-start gap-2.5 px-3 text-sm font-normal"
          aria-label="Notifications"
          onClick={() => setOpen((value) => !value)}
        >
          <Bell className="h-4 w-4 shrink-0" />
          <span className="flex-1 text-left">Notifications</span>
          {unreadCount > 0 && (
            <Badge className="h-5 min-w-5 justify-center px-1 text-xs">{unreadCount}</Badge>
          )}
        </Button>
        {panel}
      </div>
    )
  }

  return (
    <div ref={containerRef} className={cn('relative', className)}>
      <Button
        variant="ghost"
        size="icon"
        aria-label="Notifications"
        onClick={() => setOpen((value) => !value)}
      >
        <Bell className="h-4 w-4" />
        {unreadCount > 0 && (
          <Badge className="absolute -right-1 -top-1 h-5 min-w-5 justify-center px-1 text-xs">
            {unreadCount}
          </Badge>
        )}
      </Button>
      {panel}
    </div>
  )
}
