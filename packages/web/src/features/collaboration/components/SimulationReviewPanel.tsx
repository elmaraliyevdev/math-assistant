import { useState } from 'react'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ApprovalTimeline } from '@/features/collaboration/components/ApprovalTimeline'
import { PermissionActionButton } from '@/features/collaboration/components/PermissionActionButton'
import { ReviewDecisionDialog } from '@/features/collaboration/components/ReviewDecisionDialog'
import {
  useApproveSimulation,
  useSimulationWorkflow,
  useSubmitSimulationReview,
  useTransitionWorkflow,
} from '@/features/collaboration/hooks/use-collaboration'
import { getPendingApprovalStage } from '@/features/collaboration/review-workflow'
import { RoleBadge } from '@/features/organizations/components/RoleBadge'
import { useOrganizationPermissions } from '@/features/organizations/use-organizations'
import {
  canApproveReview,
  canRecordApproval,
  canReleaseSimulation,
  canRequestReview,
  PERMISSION_MESSAGES,
} from '@/lib/permissions'

interface SimulationReviewPanelProps {
  simulationId: string
  initialDialog?: 'changes' | 'approve-review' | 'reject' | null
}

export function SimulationReviewPanel({
  simulationId,
  initialDialog = null,
}: SimulationReviewPanelProps) {
  const { role } = useOrganizationPermissions()
  const workflow = useSimulationWorkflow(simulationId)
  const transition = useTransitionWorkflow(simulationId)
  const submitReview = useSubmitSimulationReview(simulationId)
  const approve = useApproveSimulation(simulationId)
  const [dialog, setDialog] = useState<
    | 'changes'
    | 'approve-review'
    | 'reject'
    | 'mathematician'
    | 'senior'
    | 'product'
    | 'producer'
    | null
  >(initialDialog)

  const status = workflow.data?.status ?? 'draft'
  const canReview = canApproveReview(role)
  const canSubmit = canRequestReview(role)
  const canRelease = canReleaseSimulation(role)
  const pendingStage = workflow.data
    ? getPendingApprovalStage(workflow.data.approvals)
    : null

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between gap-4">
          <div>
            <CardTitle>Review actions</CardTitle>
            <p className="text-sm text-muted-foreground">
              Actions available for your current role.
            </p>
          </div>
          {role && <RoleBadge role={role} />}
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap gap-2">
            {status === 'draft' && (
              <PermissionActionButton
                allowed={canSubmit}
                disabledReason={PERMISSION_MESSAGES.requestReview}
                onClick={() => transition.mutate('under_review')}
                disabled={transition.isPending}
              >
                Request review
              </PermissionActionButton>
            )}

            {status === 'under_review' && (
              <>
                <PermissionActionButton
                  allowed={canReview}
                  disabledReason={PERMISSION_MESSAGES.approveReview}
                  variant="outline"
                  onClick={() => setDialog('changes')}
                >
                  Request changes
                </PermissionActionButton>
                <PermissionActionButton
                  allowed={canReview}
                  disabledReason={PERMISSION_MESSAGES.approveReview}
                  variant="outline"
                  onClick={() => setDialog('reject')}
                >
                  Reject
                </PermissionActionButton>
                <PermissionActionButton
                  allowed={canReview}
                  disabledReason={PERMISSION_MESSAGES.approveReview}
                  onClick={() => setDialog('approve-review')}
                >
                  Approve mathematics
                </PermissionActionButton>
              </>
            )}

            {status === 'approved' && (
              <PermissionActionButton
                allowed={canReview}
                disabledReason={PERMISSION_MESSAGES.approveReview}
                onClick={() => transition.mutate('certification_ready')}
                disabled={transition.isPending}
              >
                Mark certification ready
              </PermissionActionButton>
            )}

            {status === 'certification_ready' && (
              <PermissionActionButton
                allowed={canRelease}
                disabledReason={PERMISSION_MESSAGES.releaseSimulation}
                onClick={() => transition.mutate('released')}
                disabled={transition.isPending}
              >
                Release simulation
              </PermissionActionButton>
            )}

            {pendingStage && status === 'approved' && (
              <PermissionActionButton
                allowed={canRecordApproval(role, pendingStage)}
                disabledReason={PERMISSION_MESSAGES.recordApproval}
                variant="secondary"
                onClick={() => {
                  if (pendingStage === 'mathematician') setDialog('mathematician')
                  if (pendingStage === 'senior_mathematician') setDialog('senior')
                  if (pendingStage === 'product_owner') setDialog('product')
                  if (pendingStage === 'producer') setDialog('producer')
                }}
              >
                Record {pendingStage.replaceAll('_', ' ')} approval
              </PermissionActionButton>
            )}
          </div>
        </CardContent>
      </Card>

      {workflow.data && <ApprovalTimeline approvals={workflow.data.approvals} />}

      <ReviewDecisionDialog
        open={dialog === 'changes'}
        onOpenChange={(open) => !open && setDialog(null)}
        title="Request changes"
        description="Send the simulation back to draft with feedback for the author."
        confirmLabel="Request changes"
        requireReason
        pending={submitReview.isPending}
        onConfirm={(reason) =>
          submitReview.mutate(
            { status: 'changes_requested', decisionReason: reason },
            { onSuccess: () => setDialog(null) },
          )
        }
      />

      <ReviewDecisionDialog
        open={dialog === 'reject'}
        onOpenChange={(open) => !open && setDialog(null)}
        title="Reject simulation"
        description="Reject the mathematics review and return the simulation to draft."
        confirmLabel="Reject"
        requireReason
        pending={submitReview.isPending}
        onConfirm={(reason) =>
          submitReview.mutate(
            { status: 'rejected', decisionReason: reason },
            { onSuccess: () => setDialog(null) },
          )
        }
      />

      <ReviewDecisionDialog
        open={dialog === 'approve-review'}
        onOpenChange={(open) => !open && setDialog(null)}
        title="Approve simulation"
        description="Approve the mathematics for this simulation."
        confirmLabel="Approve"
        pending={submitReview.isPending}
        onConfirm={() =>
          submitReview.mutate(
            { status: 'approved' },
            { onSuccess: () => setDialog(null) },
          )
        }
      />

      <ReviewDecisionDialog
        open={dialog === 'mathematician'}
        onOpenChange={(open) => !open && setDialog(null)}
        title="Mathematician approval"
        description="Record mathematician sign-off for this simulation."
        confirmLabel="Approve stage"
        pending={approve.isPending}
        onConfirm={() =>
          approve.mutate('mathematician', { onSuccess: () => setDialog(null) })
        }
      />

      <ReviewDecisionDialog
        open={dialog === 'senior'}
        onOpenChange={(open) => !open && setDialog(null)}
        title="Senior mathematician approval"
        description="Record senior mathematician sign-off."
        confirmLabel="Approve stage"
        pending={approve.isPending}
        onConfirm={() =>
          approve.mutate('senior_mathematician', {
            onSuccess: () => setDialog(null) },
          )
        }
      />

      <ReviewDecisionDialog
        open={dialog === 'product'}
        onOpenChange={(open) => !open && setDialog(null)}
        title="Product owner approval"
        description="Record business acceptance for this simulation."
        confirmLabel="Approve stage"
        pending={approve.isPending}
        onConfirm={() =>
          approve.mutate('product_owner', { onSuccess: () => setDialog(null) })
        }
      />

      <ReviewDecisionDialog
        open={dialog === 'producer'}
        onOpenChange={(open) => !open && setDialog(null)}
        title="Producer approval"
        description="Record producer sign-off before release."
        confirmLabel="Approve stage"
        pending={approve.isPending}
        onConfirm={() =>
          approve.mutate('producer', { onSuccess: () => setDialog(null) })
        }
      />
    </div>
  )
}
