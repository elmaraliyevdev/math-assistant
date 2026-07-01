import { Badge, statusBadgeVariant } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { formatDate } from '@/lib/utils'
import type { SimulationApproval } from '@/features/collaboration/types'

const STAGE_LABELS: Record<string, string> = {
  mathematician: 'Mathematician',
  senior_mathematician: 'Senior mathematician',
  product_owner: 'Product owner',
  producer: 'Producer',
}

const STAGE_ORDER = [
  'mathematician',
  'senior_mathematician',
  'product_owner',
  'producer',
] as const satisfies readonly SimulationApproval['approvalStage'][]

interface ApprovalTimelineProps {
  approvals: SimulationApproval[]
}

export function ApprovalTimeline({ approvals }: ApprovalTimelineProps) {
  const byStage = new Map(approvals.map((item) => [item.approvalStage, item]))

  return (
    <Card>
      <CardHeader>
        <CardTitle>Approval timeline</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {STAGE_ORDER.map((stage) => {
          const approval = byStage.get(stage)
          return (
            <div
              key={stage}
              className="flex items-center justify-between rounded-md border p-3"
            >
              <div>
                <p className="font-medium">{STAGE_LABELS[stage]}</p>
                {approval ? (
                  <p className="text-xs text-muted-foreground">
                    Approved {formatDate(approval.approvedAt)}
                  </p>
                ) : (
                  <p className="text-xs text-muted-foreground">Pending</p>
                )}
              </div>
              <Badge variant={statusBadgeVariant(approval ? 'completed' : 'pending')}>
                {approval ? 'Approved' : 'Pending'}
              </Badge>
            </div>
          )
        })}
      </CardContent>
    </Card>
  )
}
