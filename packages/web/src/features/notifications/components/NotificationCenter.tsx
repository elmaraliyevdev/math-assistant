import { Bell } from 'lucide-react'
import { useState } from 'react'
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
import { formatDate } from '@/lib/utils'

export function NotificationCenter() {
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

  return (
    <div className="relative">
      <Button
        variant="ghost"
        size="icon"
        aria-label="Notifications"
        onClick={() => setOpen((value) => !value)}
      >
        <Bell className="h-4 w-4" />
        {(notifications.data?.unreadCount ?? 0) > 0 && (
          <Badge className="absolute -right-1 -top-1 h-5 min-w-5 justify-center px-1 text-xs">
            {notifications.data?.unreadCount}
          </Badge>
        )}
      </Button>
      {open && (
        <div className="absolute right-0 z-50 mt-2 w-96 rounded-lg border bg-card p-4 shadow-lg">
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
                  className={`w-full rounded-md border p-3 text-left text-sm transition-colors hover:bg-accent ${
                    item.readAt
                      ? 'opacity-70'
                      : isActionableReview
                        ? 'border-amber-500/40 bg-amber-500/5'
                        : 'border-primary/30'
                  }`}
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
                  <p className="mt-1 text-xs text-muted-foreground">
                    {formatDate(item.createdAt)}
                  </p>
                </button>
              )
            })}
            {!notifications.isLoading &&
              (notifications.data?.items.length ?? 0) === 0 && (
                <p className="text-sm text-muted-foreground">No notifications.</p>
              )}
          </div>
        </div>
      )}
    </div>
  )
}
