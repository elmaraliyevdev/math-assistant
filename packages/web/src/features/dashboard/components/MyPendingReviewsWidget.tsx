import { Link } from '@tanstack/react-router'

import { Button } from '@/components/ui/button'
import { EmptyState } from '@/components/empty-state'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import type { CollaborationSimulationSummary } from '@/features/collaboration/api/collaboration-api'
import { useOrganizationPermissions } from '@/features/organizations/use-organizations'
import { canApproveReview } from '@/lib/permissions'
import { formatDate } from '@/lib/utils'

interface MyPendingReviewsWidgetProps {
  items?: CollaborationSimulationSummary[]
  loading?: boolean
}

export function MyPendingReviewsWidget({
  items,
  loading,
}: MyPendingReviewsWidgetProps) {
  const { role } = useOrganizationPermissions()
  const canReview = canApproveReview(role)

  return (
    <Card>
      <CardHeader>
        <CardTitle>My pending reviews</CardTitle>
        <p className="text-sm text-muted-foreground">
          Simulations waiting for your review decision.
        </p>
      </CardHeader>
      <CardContent className="space-y-3">
        {loading &&
          Array.from({ length: 2 }).map((_, index) => (
            <Skeleton key={index} className="h-16 w-full" />
          ))}
        {!loading && !items?.length && (
          <EmptyState
            title={
              canReview ? 'No pending reviews' : 'Review access required'
            }
            description={
              canReview
                ? 'Simulations you can approve will appear here when they enter the review workflow.'
                : 'Only organization admins and owners can approve simulations. Contact your workspace admin for access.'
            }
            actions={
              canReview ? (
                <>
                  <Button size="sm" asChild>
                    <Link to="/simulations">Browse simulations</Link>
                  </Button>
                  <Button size="sm" variant="outline" asChild>
                    <Link to="/dashboard">Go to dashboard</Link>
                  </Button>
                </>
              ) : (
                <Button size="sm" variant="outline" asChild>
                  <Link to="/settings" search={{ section: 'team' }}>
                    Team settings
                  </Link>
                </Button>
              )
            }
            className="border-none p-4"
          />
        )}
        {items?.map((item) => (
          <div
            key={item.simulationId}
            className="flex flex-col gap-3 rounded-md border p-3 sm:flex-row sm:items-center sm:justify-between"
          >
            <div>
              <p className="font-medium capitalize">
                {item.workflowStatus.replaceAll('_', ' ')}
              </p>
              <p className="text-xs text-muted-foreground">
                {item.updatedAt ? formatDate(item.updatedAt) : item.simulationId}
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button size="sm" variant="outline" asChild>
                <Link
                  to="/simulations/$simulationId/review"
                  params={{ simulationId: item.simulationId }}
                >
                  Review
                </Link>
              </Button>
              {canReview && (
                <>
                  <Button size="sm" asChild>
                    <Link
                      to="/simulations/$simulationId/review"
                      params={{ simulationId: item.simulationId }}
                      search={{ action: 'approve' }}
                    >
                      Approve
                    </Link>
                  </Button>
                  <Button size="sm" variant="secondary" asChild>
                    <Link
                      to="/simulations/$simulationId/review"
                      params={{ simulationId: item.simulationId }}
                      search={{ action: 'changes' }}
                    >
                      Request Changes
                    </Link>
                  </Button>
                </>
              )}
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
