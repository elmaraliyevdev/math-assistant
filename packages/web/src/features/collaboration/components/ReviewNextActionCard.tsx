import { Badge, statusBadgeVariant } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { PermissionActionButton } from '@/features/collaboration/components/PermissionActionButton'
import { getReviewNextAction } from '@/features/collaboration/review-workflow'
import type { SimulationWorkflow } from '@/features/collaboration/api/collaboration-api'
import type { OrganizationRole } from '@/types/api'

interface ReviewNextActionCardProps {
  workflow?: SimulationWorkflow
  role?: OrganizationRole
  onAction?: (actionType: NonNullable<ReturnType<typeof getReviewNextAction>['actionType']>) => void
  pending?: boolean
}

export function ReviewNextActionCard({
  workflow,
  role,
  onAction,
  pending = false,
}: ReviewNextActionCardProps) {
  const nextAction = getReviewNextAction(workflow, role)

  return (
    <Card className="border-primary/30 bg-primary/5">
      <CardHeader className="flex flex-row items-start justify-between gap-4">
        <div>
          <CardTitle>Your next action</CardTitle>
          <p className="mt-1 text-sm text-muted-foreground">{nextAction.description}</p>
        </div>
        <Badge variant={statusBadgeVariant(nextAction.canPerform ? 'running' : 'pending')}>
          {nextAction.title}
        </Badge>
      </CardHeader>
      {nextAction.actionLabel && onAction && nextAction.actionType && (
        <CardContent>
          <PermissionActionButton
            allowed={nextAction.canPerform}
            disabledReason={nextAction.disabledReason}
            disabled={pending}
            onClick={() => onAction(nextAction.actionType!)}
          >
            {nextAction.actionLabel}
          </PermissionActionButton>
        </CardContent>
      )}
      {!nextAction.canPerform && nextAction.disabledReason && (
        <CardContent>
          <p className="text-sm text-muted-foreground">{nextAction.disabledReason}</p>
        </CardContent>
      )}
    </Card>
  )
}

export function PendingApprovalsNotice({
  workflow,
}: {
  workflow?: SimulationWorkflow
}) {
  if (!workflow || workflow.status === 'released') {
    return null
  }

  const pendingReviews = workflow.reviews.filter((item) => item.status === 'pending')
  if (pendingReviews.length === 0 && workflow.status !== 'under_review') {
    return null
  }

  return (
    <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 p-4">
      <div className="flex items-center gap-2">
        <Badge variant={statusBadgeVariant('running')}>Pending approval</Badge>
        <p className="text-sm font-medium">
          {workflow.status === 'under_review'
            ? 'This simulation is waiting for a review decision.'
            : `${pendingReviews.length} review decision(s) are still pending.`}
        </p>
      </div>
    </div>
  )
}
