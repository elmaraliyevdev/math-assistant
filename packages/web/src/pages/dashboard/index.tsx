import { Link } from '@tanstack/react-router'
import type { ReactNode } from 'react'
import { ArrowRight, FlaskConical, Gamepad2 } from 'lucide-react'

import { Badge, statusBadgeVariant } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { SimulationQueueWidget } from '@/features/distributed/components/SimulationQueueWidget'
import { WorkerStatusWidget } from '@/features/distributed/components/WorkerStatusWidget'
import { MyPendingReviewsWidget } from '@/features/dashboard/components/MyPendingReviewsWidget'
import { MetricsOverview } from '@/features/dashboard/components/MetricsOverview'
import { useDashboardSummary } from '@/features/dashboard/hooks/use-dashboard'
import type { CollaborationSimulationSummary } from '@/features/collaboration/api/collaboration-api'
import { useMe } from '@/features/auth/use-auth'
import { formatDate, formatPercent } from '@/lib/utils'

export function DashboardPage() {
  const summary = useDashboardSummary()
  const me = useMe()
  const isOwner = me.data?.organizations.some((org) => org.role === 'owner')

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Dashboard</h2>
        <p className="text-muted-foreground">
          Overview of simulations, activity, and notifications.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total simulations"
          value={summary.data?.totalSimulations}
          loading={summary.isLoading}
          icon={<FlaskConical className="h-4 w-4" />}
        />
        <StatCard
          title="Active simulations"
          value={summary.data?.activeSimulations}
          loading={summary.isLoading}
          icon={<FlaskConical className="h-4 w-4" />}
        />
        <StatCard
          title="Average RTP"
          value={
            summary.data?.averageRtp != null
              ? formatPercent(summary.data.averageRtp)
              : '—'
          }
          loading={summary.isLoading}
          icon={<FlaskConical className="h-4 w-4" />}
        />
        <StatCard
          title="Games"
          value={summary.data?.totalGames}
          loading={summary.isLoading}
          icon={<Gamepad2 className="h-4 w-4" />}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <RecentCard
          title="Recent activity"
          loading={summary.isLoading}
          empty="No recent activity."
          items={summary.data?.recentActivity.map((entry) => ({
            id: entry.id,
            title: entry.action,
            subtitle: `${entry.entityType}${entry.entityId ? ` · ${entry.entityId}` : ''}`,
            meta: formatDate(entry.createdAt),
          }))}
          footerTo="/audit"
        />
        <RecentCard
          title="Recent notifications"
          loading={summary.isLoading}
          empty="No notifications yet."
          items={summary.data?.recentNotifications.map((item) => ({
            id: item.id,
            title: item.title,
            subtitle: item.message,
            meta: formatDate(item.createdAt),
            badge: item.readAt ? 'read' : 'new',
          }))}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <RecentCard
          title="Recent simulations"
          loading={summary.isLoading}
          empty="No simulations yet."
          items={summary.data?.recentSimulations.map((item) => ({
            id: item.simulationId,
            title: item.gameName
              ? `${item.gameName} ${item.gameVersionLabel ?? ''}`.trim()
              : item.simulationId,
            subtitle: `${item.spinCount.toLocaleString()} spins · ${item.status}`,
            meta: formatDate(item.createdAt),
            badge:
              item.withinRtpTolerance === false
                ? 'rtp drift'
                : item.workflowStatus.replaceAll('_', ' '),
          }))}
        />
        <RecentCard
          title="Recommended next actions"
          loading={summary.isLoading}
          empty="No recommendations right now."
          items={summary.data?.recommendedActions.map((action) => ({
            id: action.id,
            title: action.label,
            subtitle: action.description,
            meta: action.href,
          }))}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <MyPendingReviewsWidget
          items={summary.data?.myPendingReviews}
          loading={summary.isLoading}
        />
        <CollaborationCard
          title="Pending reviews"
          loading={summary.isLoading}
          empty="No simulations awaiting review."
          items={summary.data?.pendingReviews}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <CollaborationCard
          title="Certification ready"
          loading={summary.isLoading}
          empty="No simulations ready for certification."
          items={summary.data?.certificationReady}
        />
        <CollaborationCard
          title="Recently approved"
          loading={summary.isLoading}
          empty="No recently approved simulations."
          items={summary.data?.recentlyApproved}
        />
        <RecentCard
          title="Simulations outside RTP tolerance"
          loading={summary.isLoading}
          empty="All recent completed simulations are within tolerance."
          items={summary.data?.outsideRtpTolerance.map((item) => ({
            id: item.simulationId,
            title: item.gameName
              ? `${item.gameName} ${item.gameVersionLabel ?? ''}`.trim()
              : item.simulationId,
            subtitle: item.rtp != null ? `RTP ${(item.rtp * 100).toFixed(2)}%` : 'RTP unavailable',
            meta: formatDate(item.createdAt),
            badge: 'review',
          }))}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <SimulationQueueWidget />
        <WorkerStatusWidget />
      </div>

      {isOwner && <MetricsOverview />}
    </div>
  )
}

function StatCard({
  title,
  value,
  loading,
  icon,
}: {
  title: string
  value?: number | string
  loading: boolean
  icon: ReactNode
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        {loading ? (
          <Skeleton className="h-8 w-16" />
        ) : (
          <p className="text-3xl font-bold">{value ?? 0}</p>
        )}
      </CardContent>
    </Card>
  )
}

function CollaborationCard({
  title,
  loading,
  empty,
  items,
}: {
  title: string
  loading: boolean
  empty: string
  items?: CollaborationSimulationSummary[]
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {loading &&
          Array.from({ length: 2 }).map((_, index) => (
            <Skeleton key={index} className="h-12 w-full" />
          ))}
        {!loading && !items?.length && (
          <p className="text-sm text-muted-foreground">{empty}</p>
        )}
        {items?.map((item) => (
          <Link
            key={item.simulationId}
            to="/simulations/$simulationId/review"
            params={{ simulationId: item.simulationId }}
            className="block rounded-md border p-3 hover:bg-muted/50"
          >
            <p className="font-medium capitalize">
              {item.workflowStatus.replaceAll('_', ' ')}
            </p>
            <p className="text-xs text-muted-foreground">
              {item.updatedAt ? formatDate(item.updatedAt) : item.simulationId}
            </p>
          </Link>
        ))}
      </CardContent>
    </Card>
  )
}

function RecentCard({
  title,
  loading,
  empty,
  items,
  footerTo,
}: {
  title: string
  loading: boolean
  empty: string
  items?: Array<{
    id: string
    title: string
    subtitle: string
    meta: string
    badge?: string
  }>
  footerTo?: string
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>{title}</CardTitle>
        {footerTo && (
          <Button variant="ghost" size="sm" asChild>
            <Link to={footerTo}>
              View all
              <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
        )}
      </CardHeader>
      <CardContent className="space-y-3">
        {loading &&
          Array.from({ length: 3 }).map((_, index) => (
            <Skeleton key={index} className="h-12 w-full" />
          ))}
        {!loading && !items?.length && (
          <p className="text-sm text-muted-foreground">{empty}</p>
        )}
        {items?.map((item) => (
          <div
            key={item.id}
            className="flex items-center justify-between rounded-md border p-3"
          >
            <div>
              <p className="font-medium">{item.title}</p>
              <p className="text-sm text-muted-foreground">{item.subtitle}</p>
              <p className="text-xs text-muted-foreground">{item.meta}</p>
            </div>
            {item.badge && (
              <Badge variant={statusBadgeVariant(item.badge)}>{item.badge}</Badge>
            )}
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
