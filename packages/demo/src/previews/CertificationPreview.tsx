'use client'

import { Badge, statusBadgeVariant } from '@/components/ui/badge'
import {
  WORKFLOW_STEP_LABELS,
  WORKFLOW_STEPS,
} from '@/features/collaboration/review-workflow'

import { demoSimulationActivity, demoSimulationWorkflow } from '../data/workflow'

const STAGE_LABELS: Record<string, string> = {
  mathematician: 'Elena K.',
  senior_mathematician: 'Marcus T.',
  product_owner: 'Sarah L.',
  producer: 'James R.',
}

const STAGE_ORDER = [
  'mathematician',
  'senior_mathematician',
  'product_owner',
  'producer',
] as const

/** Marketing composition: workflow chips + reviewers + audit trail. */
export function CertificationPreview() {
  const { status, approvals } = demoSimulationWorkflow
  const currentIndex = WORKFLOW_STEPS.indexOf(
    status as (typeof WORKFLOW_STEPS)[number],
  )
  const approvedStages = new Set(approvals.map((item) => item.approvalStage))
  const auditItems = demoSimulationActivity.slice(0, 3)

  return (
    <div className="demo-preview-shell">
      <div className="demo-preview-feature demo-cert-preview">
        <div className="demo-cert-preview__workflow">
          {WORKFLOW_STEPS.map((step, index) => {
            const isComplete = currentIndex > index
            const isCurrent = currentIndex === index
            const variant = isCurrent
              ? 'running'
              : isComplete
                ? 'completed'
                : 'pending'
            return (
              <Badge
                key={step}
                variant={statusBadgeVariant(variant)}
                className={isCurrent ? 'demo-cert-preview__chip--current' : undefined}
              >
                {WORKFLOW_STEP_LABELS[step]}
              </Badge>
            )
          })}
        </div>

        <ul className="demo-cert-preview__reviewers">
          {STAGE_ORDER.map((stage) => {
            const approved = approvedStages.has(stage)
            return (
              <li
                key={stage}
                className={
                  approved
                    ? 'demo-cert-preview__reviewer demo-cert-preview__reviewer--done'
                    : 'demo-cert-preview__reviewer demo-cert-preview__reviewer--pending demo-animate-approval-pulse'
                }
              >
                <span className="demo-cert-preview__reviewer-name">
                  {STAGE_LABELS[stage]}
                </span>
                <span className="demo-cert-preview__reviewer-status">
                  {approved ? 'Approved' : 'Pending'}
                </span>
              </li>
            )
          })}
        </ul>

        <ul className="demo-cert-preview__audit" aria-label="Audit trail">
          {auditItems.map((entry) => {
            const rtp =
              entry.metadata && 'rtp' in entry.metadata
                ? String(entry.metadata.rtp)
                : null
            return (
              <li key={entry.id}>
                <span>{entry.action.replaceAll('_', ' ')}</span>
                {rtp ? (
                  <span className="text-muted-foreground"> · {rtp}</span>
                ) : null}
              </li>
            )
          })}
        </ul>
      </div>
    </div>
  )
}
