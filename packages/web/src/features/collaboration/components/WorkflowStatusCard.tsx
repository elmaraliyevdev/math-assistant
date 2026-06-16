import { Badge, statusBadgeVariant } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  WORKFLOW_STEP_LABELS,
  WORKFLOW_STEPS,
} from '@/features/collaboration/review-workflow'

interface WorkflowStatusCardProps {
  status: string
}

export function WorkflowStatusCard({ status }: WorkflowStatusCardProps) {
  const currentIndex = WORKFLOW_STEPS.indexOf(
    status as (typeof WORKFLOW_STEPS)[number],
  )

  return (
    <Card>
      <CardHeader>
        <CardTitle>Workflow progression</CardTitle>
        <p className="text-sm text-muted-foreground">
          Draft → Under Review → Approved → Certification Ready → Released
        </p>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex flex-wrap items-center gap-2">
          {WORKFLOW_STEPS.map((step, index) => {
            const isComplete = currentIndex > index
            const isCurrent = currentIndex === index
            const variant = isCurrent
              ? 'running'
              : isComplete
                ? 'completed'
                : 'pending'
            return (
              <div key={step} className="flex items-center gap-2">
                <Badge
                  variant={statusBadgeVariant(variant)}
                  className={isCurrent ? 'ring-2 ring-primary/40' : undefined}
                >
                  {WORKFLOW_STEP_LABELS[step]}
                </Badge>
                {index < WORKFLOW_STEPS.length - 1 && (
                  <span
                    className={
                      isComplete ? 'text-foreground' : 'text-muted-foreground'
                    }
                  >
                    →
                  </span>
                )}
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
