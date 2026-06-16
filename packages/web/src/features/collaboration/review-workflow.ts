import type { OrganizationRole } from '@/types/api'
import type { SimulationApproval, SimulationWorkflow } from '@/features/collaboration/api/collaboration-api'
import {
  canApproveReview,
  canRecordApproval,
  canReleaseSimulation,
  canRequestReview,
} from '@/lib/permissions'

export const WORKFLOW_STEPS = [
  'draft',
  'under_review',
  'approved',
  'certification_ready',
  'released',
] as const

export const WORKFLOW_STEP_LABELS: Record<string, string> = {
  draft: 'Draft',
  under_review: 'Under Review',
  approved: 'Approved',
  certification_ready: 'Certification Ready',
  released: 'Released',
}

export interface ReviewNextAction {
  title: string
  description: string
  actionLabel?: string
  actionType?:
    | 'request_review'
    | 'approve'
    | 'request_changes'
    | 'reject'
    | 'certification_ready'
    | 'release'
    | 'stage_approval'
  stage?: SimulationApproval['approvalStage']
  canPerform: boolean
  disabledReason?: string
}

const STAGE_ORDER = [
  'mathematician',
  'senior_mathematician',
  'product_owner',
  'producer',
] as const satisfies readonly SimulationApproval['approvalStage'][]

export function getPendingApprovalStage(
  approvals: SimulationApproval[],
): SimulationApproval['approvalStage'] | null {
  const completed = new Set(approvals.map((item) => item.approvalStage))
  return (
    STAGE_ORDER.find((stage) => !completed.has(stage)) ?? null
  )
}

export function getReviewNextAction(
  workflow: SimulationWorkflow | undefined,
  role: OrganizationRole | undefined,
): ReviewNextAction {
  const status = workflow?.status ?? 'draft'
  const pendingStage = workflow
    ? getPendingApprovalStage(workflow.approvals)
    : null

  if (status === 'draft') {
    if (canRequestReview(role)) {
      return {
        title: 'Submit for review',
        description:
          'Request mathematician review when calibration results look ready.',
        actionLabel: 'Request review',
        actionType: 'request_review',
        canPerform: true,
      }
    }
    return {
      title: 'Waiting for submission',
      description: 'A developer must submit this simulation for review.',
      canPerform: false,
      disabledReason: 'Only developers and above can submit simulations for review.',
    }
  }

  if (status === 'under_review') {
    if (canApproveReview(role)) {
      return {
        title: 'Complete mathematics review',
        description:
          'Approve the simulation or request changes with clear feedback.',
        actionLabel: 'Approve mathematics',
        actionType: 'approve',
        canPerform: true,
      }
    }
    return {
      title: 'Awaiting reviewer decision',
      description: 'An admin or owner will approve or request changes.',
      canPerform: false,
      disabledReason: 'Only admins and owners can approve or request changes.',
    }
  }

  if (status === 'approved') {
    if (pendingStage) {
      const canRecord = canRecordApproval(role, pendingStage)
      return {
        title: 'Record stakeholder approval',
        description: `Next required sign-off: ${pendingStage.replaceAll('_', ' ')}.`,
        actionLabel: 'Record approval',
        actionType: 'stage_approval',
        stage: pendingStage,
        canPerform: canRecord,
        disabledReason: canRecord
          ? undefined
          : 'You do not have permission to record this approval stage.',
      }
    }
    if (canApproveReview(role)) {
      return {
        title: 'Mark certification ready',
        description: 'All review stages are complete. Prepare for certification.',
        actionLabel: 'Mark certification ready',
        actionType: 'certification_ready',
        canPerform: true,
      }
    }
    return {
      title: 'Awaiting certification handoff',
      description: 'An admin or owner will mark this simulation certification ready.',
      canPerform: false,
      disabledReason: 'Only admins and owners can mark certification ready.',
    }
  }

  if (status === 'certification_ready') {
    if (canReleaseSimulation(role)) {
      return {
        title: 'Release simulation',
        description: 'Release the certified simulation to production stakeholders.',
        actionLabel: 'Release simulation',
        actionType: 'release',
        canPerform: true,
      }
    }
    return {
      title: 'Awaiting release',
      description: 'Only the organization owner can release this simulation.',
      canPerform: false,
      disabledReason: 'Only the organization owner can release a simulation.',
    }
  }

  return {
    title: 'Workflow complete',
    description: 'This simulation has been released.',
    canPerform: false,
  }
}

export function isReviewNotification(type: string): boolean {
  return [
    'review_requested',
    'changes_requested',
    'simulation_approved',
    'certification_ready',
  ].includes(type)
}

export function reviewNotificationHref(
  entityType: string | null | undefined,
  entityId: string | null | undefined,
): string | null {
  if (entityType === 'simulation' && entityId) {
    return `/simulations/${entityId}/review`
  }
  return null
}
