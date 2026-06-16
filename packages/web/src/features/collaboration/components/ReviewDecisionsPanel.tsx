import { Badge, statusBadgeVariant } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { RoleBadge } from '@/features/organizations/components/RoleBadge'
import type { SimulationReview } from '@/features/collaboration/api/collaboration-api'
import type { OrganizationRole } from '@/types/api'
import { formatDate } from '@/lib/utils'

interface ReviewDecisionsPanelProps {
  reviews: SimulationReview[]
}

function reviewStatusVariant(status: string) {
  if (status === 'approved') return 'completed'
  if (status === 'rejected' || status === 'changes_requested') return 'failed'
  return 'pending'
}

export function ReviewDecisionsPanel({ reviews }: ReviewDecisionsPanelProps) {
  if (reviews.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Review decisions</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">No review decisions yet.</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Review decisions</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {reviews.map((review) => (
          <div key={review.id} className="rounded-lg border p-4">
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant={statusBadgeVariant(reviewStatusVariant(review.status))}>
                {review.status.replaceAll('_', ' ')}
              </Badge>
              {review.reviewerRole && (
                <RoleBadge role={review.reviewerRole as OrganizationRole} />
              )}
            </div>
            <p className="mt-2 text-sm font-medium">
              {review.reviewerName ?? review.reviewerEmail ?? review.reviewerId}
            </p>
            {review.decisionReason && (
              <p className="mt-2 text-sm text-muted-foreground">{review.decisionReason}</p>
            )}
            <p className="mt-2 text-xs text-muted-foreground">
              {formatDate(review.createdAt)}
            </p>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
