import { Link, useParams, useSearch } from '@tanstack/react-router'

import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import {
  ActivityTimeline,
  CommentsPanel,
  PendingApprovalsNotice,
  ReviewDecisionsPanel,
  ReviewNextActionCard,
  SimulationReviewPanel,
  WorkflowStatusCard,
} from '@/features/collaboration/components'
import { useSimulationWorkflow } from '@/features/collaboration/hooks/use-collaboration'
import { RoleBadge } from '@/features/organizations/components/RoleBadge'
import { useOrganizationPermissions } from '@/features/organizations/use-organizations'
import { CertificationReadinessPanel } from '@/features/mathematics/components/CertificationReadinessPanel'
import { useSimulation } from '@/features/simulations/hooks/use-simulations'
import { useSimulationCalibration } from '@/features/workbench/hooks/use-workbench'

export function SimulationReviewPage() {
  const { simulationId } = useParams({ strict: false }) as {
    simulationId: string
  }
  const search = useSearch({ strict: false }) as { action?: string }
  const simulation = useSimulation(simulationId, true)
  const workflow = useSimulationWorkflow(simulationId, Boolean(simulation.data))
  const calibration = useSimulationCalibration(
    simulation.data?.gameVersionId,
    simulationId,
    simulation.data?.status === 'completed',
  )
  const { role } = useOrganizationPermissions()

  const initialDialog =
    search.action === 'approve'
      ? 'approve-review'
      : search.action === 'changes'
        ? 'changes'
        : null

  if (simulation.isLoading || workflow.isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-40 w-full" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-2xl font-bold tracking-tight">
              Simulation review
            </h2>
            {role && <RoleBadge role={role} />}
          </div>
          <p className="text-muted-foreground">
            Collaborate on mathematics review, approvals, and release workflow.
          </p>
        </div>
        <Button variant="outline" asChild>
          <Link to="/simulations/$simulationId" params={{ simulationId }}>
            Back to simulation
          </Link>
        </Button>
      </div>

      <ReviewNextActionCard workflow={workflow.data} role={role} />
      <PendingApprovalsNotice workflow={workflow.data} />

      {calibration.data?.certificationReadiness && (
        <CertificationReadinessPanel
          readiness={calibration.data.certificationReadiness}
        />
      )}

      {workflow.data && <WorkflowStatusCard status={workflow.data.status} />}

      <div className="grid gap-6 lg:grid-cols-2">
        <SimulationReviewPanel
          simulationId={simulationId}
          initialDialog={initialDialog}
        />
        <CommentsPanel simulationId={simulationId} />
      </div>

      {workflow.data && <ReviewDecisionsPanel reviews={workflow.data.reviews} />}

      <ActivityTimeline simulationId={simulationId} />
    </div>
  )
}
