import { describe, expect, it } from 'vitest'

import {
  getPendingApprovalStage,
  getReviewNextAction,
  isReviewNotification,
  reviewNotificationHref,
} from '@/features/collaboration/review-workflow'

describe('review-workflow helpers', () => {
  it('covers draft, approved, and certification paths', () => {
    expect(getReviewNextAction(undefined, 'viewer').canPerform).toBe(false)
    expect(
      getReviewNextAction(
        { simulationId: 's', status: 'approved', reviews: [], approvals: [
          { id: '1', simulationId: 's', approvedBy: 'u', approvalStage: 'mathematician', approvedAt: '' },
          { id: '2', simulationId: 's', approvedBy: 'u', approvalStage: 'senior_mathematician', approvedAt: '' },
          { id: '3', simulationId: 's', approvedBy: 'u', approvalStage: 'product_owner', approvedAt: '' },
          { id: '4', simulationId: 's', approvedBy: 'u', approvalStage: 'producer', approvedAt: '' },
        ] },
        'admin',
      ).actionType,
    ).toBe('certification_ready')
    expect(
      getReviewNextAction(
        { simulationId: 's', status: 'approved', reviews: [], approvals: [] },
        'developer',
      ).canPerform,
    ).toBe(false)
    expect(
      getReviewNextAction(
        { simulationId: 's', status: 'certification_ready', reviews: [], approvals: [] },
        'admin',
      ).disabledReason,
    ).toMatch(/owner/i)
  })

  it('handles stage approval permissions and notification helpers', () => {
    expect(getPendingApprovalStage([])).toBe('mathematician')
    expect(getPendingApprovalStage([
      { id: '1', simulationId: 's', approvedBy: 'u', approvalStage: 'mathematician', approvedAt: '' },
      { id: '2', simulationId: 's', approvedBy: 'u', approvalStage: 'senior_mathematician', approvedAt: '' },
      { id: '3', simulationId: 's', approvedBy: 'u', approvalStage: 'product_owner', approvedAt: '' },
      { id: '4', simulationId: 's', approvedBy: 'u', approvalStage: 'producer', approvedAt: '' },
    ])).toBeNull()
    expect(isReviewNotification('other')).toBe(false)
    expect(reviewNotificationHref('game', 'id')).toBeNull()
  })
})
