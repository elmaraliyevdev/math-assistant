import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi, beforeEach } from 'vitest'

import { ApprovalTimeline } from '@/features/collaboration/components/ApprovalTimeline'
import { ActivityTimeline } from '@/features/collaboration/components/ActivityTimeline'
import { CommentsPanel } from '@/features/collaboration/components/CommentsPanel'
import { PermissionActionButton } from '@/features/collaboration/components/PermissionActionButton'
import { ReviewDecisionDialog } from '@/features/collaboration/components/ReviewDecisionDialog'
import { ReviewDecisionsPanel } from '@/features/collaboration/components/ReviewDecisionsPanel'
import {
  PendingApprovalsNotice,
  ReviewNextActionCard,
} from '@/features/collaboration/components/ReviewNextActionCard'
import { SimulationReviewPanel } from '@/features/collaboration/components/SimulationReviewPanel'
import { WorkflowStatusCard } from '@/features/collaboration/components/WorkflowStatusCard'
import { MyPendingReviewsWidget } from '@/features/dashboard/components/MyPendingReviewsWidget'
import {
  getPendingApprovalStage,
  getReviewNextAction,
  isReviewNotification,
  reviewNotificationHref,
} from '@/features/collaboration/review-workflow'
import type { SimulationWorkflow } from '@/features/collaboration/api/collaboration-api'
import { useSimulationActivity } from '@/features/collaboration/hooks/use-collaboration'

const submitReviewMutate = vi.hoisted(() =>
  vi.fn((_payload: unknown, opts?: { onSuccess?: () => void }) => opts?.onSuccess?.()),
)
const approveMutate = vi.hoisted(() =>
  vi.fn((_stage: unknown, opts?: { onSuccess?: () => void }) => opts?.onSuccess?.()),
)
const workflowState = vi.hoisted(() => ({
  status: 'under_review' as SimulationWorkflow['status'],
  approvals: [] as SimulationWorkflow['approvals'],
  role: 'admin' as 'admin' | 'developer' | 'owner' | 'viewer',
}))
const transitionMutate = vi.hoisted(() => vi.fn())
const addCommentMutate = vi.hoisted(() => vi.fn((_content: string, opts?: { onSuccess?: () => void }) => opts?.onSuccess?.()))

vi.mock('@tanstack/react-router', () => ({
  Link: ({
    children,
    to,
    params,
  }: {
    children: React.ReactNode
    to: string
    params?: { simulationId?: string }
    search?: Record<string, string>
  }) => (
    <a
      href={
        params?.simulationId
          ? to.replace('$simulationId', params.simulationId)
          : to
      }
    >
      {children}
    </a>
  ),
  useNavigate: () => vi.fn(),
  useParams: () => ({ simulationId: 'sim-1' }),
  useSearch: () => ({}),
}))

vi.mock('@/features/organizations/use-organizations', () => ({
  useOrganizationPermissions: () => ({ role: workflowState.role }),
}))

vi.mock('@/features/collaboration/hooks/use-collaboration', () => ({
  useSimulationWorkflow: () => ({
    data: {
      simulationId: 'sim-1',
      status: workflowState.status,
      reviews: [
        {
          id: 'review-1',
          simulationId: 'sim-1',
          reviewerId: 'user-2',
          reviewerName: 'Reviewer',
          reviewerEmail: 'reviewer@example.com',
          reviewerRole: 'admin',
          status: 'pending',
          decisionReason: null,
          createdAt: '2026-01-01T00:00:00Z',
          updatedAt: '2026-01-01T00:00:00Z',
        },
      ],
      approvals: workflowState.approvals,
    } satisfies SimulationWorkflow,
    isLoading: false,
  }),
  useTransitionWorkflow: () => ({ mutate: transitionMutate, isPending: false }),
  useSubmitSimulationReview: () => ({ mutate: submitReviewMutate, isPending: false }),
  useApproveSimulation: () => ({ mutate: approveMutate, isPending: false }),
  useSimulationComments: () => ({
    data: {
      items: [
        {
          id: 'comment-1',
          simulationId: 'sim-1',
          userId: 'user-1',
          authorName: 'Alice',
          authorEmail: 'alice@example.com',
          authorRole: 'developer',
          content: 'Please review scatter frequency.',
          createdAt: '2026-01-01T00:00:00Z',
        },
      ],
    },
    isLoading: false,
  }),
  useAddSimulationComment: () => ({ mutate: addCommentMutate, isPending: false }),
  useSimulationActivity: vi.fn(() => ({
    data: {
      items: [
        {
          id: 'activity-1',
          simulationId: 'sim-1',
          actorId: 'user-1',
          action: 'review_approved',
          metadata: null,
          createdAt: '2026-01-01T00:00:00Z',
        },
      ],
    },
    isLoading: false,
  })),
}))

function renderWithQuery(ui: React.ReactNode) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })
  return render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>)
}

beforeEach(() => {
  workflowState.status = 'under_review'
  workflowState.approvals = []
  workflowState.role = 'admin'
})

describe('review workflow utilities', () => {
  it('computes next action for reviewers', () => {
    const action = getReviewNextAction(
      { simulationId: 'sim-1', status: 'under_review', reviews: [], approvals: [] },
      'admin',
    )
    expect(action.actionType).toBe('approve')
    expect(action.canPerform).toBe(true)
  })

  it('blocks developers from approving', () => {
    const action = getReviewNextAction(
      { simulationId: 'sim-1', status: 'under_review', reviews: [], approvals: [] },
      'developer',
    )
    expect(action.canPerform).toBe(false)
    expect(action.disabledReason).toMatch(/admins and owners/i)
  })

  it('guides draft submitters and certification owners', () => {
    expect(getReviewNextAction(undefined, 'developer').actionType).toBe('request_review')
    expect(getReviewNextAction(
      { simulationId: 'sim-1', status: 'certification_ready', reviews: [], approvals: [] },
      'owner',
    ).actionType).toBe('release')
    expect(getReviewNextAction(
      { simulationId: 'sim-1', status: 'released', reviews: [], approvals: [] },
      'owner',
    ).title).toBe('Workflow complete')
  })

  it('guides approved workflow with pending stage approvals', () => {
    const action = getReviewNextAction(
      {
        simulationId: 'sim-1',
        status: 'approved',
        reviews: [],
        approvals: [],
      },
      'admin',
    )
    expect(action.actionType).toBe('stage_approval')
    expect(action.stage).toBe('mathematician')
  })

  it('finds pending approval stage and review notification links', () => {
    expect(
      getPendingApprovalStage([
        {
          id: 'a-1',
          simulationId: 'sim-1',
          approvedBy: 'user-1',
          approvalStage: 'mathematician',
          approvedAt: '2026-01-01T00:00:00Z',
        },
      ]),
    ).toBe('senior_mathematician')
    expect(isReviewNotification('review_requested')).toBe(true)
    expect(reviewNotificationHref('simulation', 'sim-1')).toBe(
      '/simulations/sim-1/review',
    )
  })
})

describe('approval workflow components', () => {
  it('renders workflow progression', () => {
    render(<WorkflowStatusCard status="under_review" />)
    expect(screen.getByText('Workflow progression')).toBeInTheDocument()
    expect(screen.getByText('Under Review')).toBeInTheDocument()
  })

  it('renders next action card and pending notice', () => {
    render(
      <ReviewNextActionCard
        workflow={{
          simulationId: 'sim-1',
          status: 'under_review',
          reviews: [],
          approvals: [],
        }}
        role="admin"
      />,
    )
    expect(screen.getByText(/your next action/i)).toBeInTheDocument()
    render(
      <PendingApprovalsNotice
        workflow={{
          simulationId: 'sim-1',
          status: 'under_review',
          reviews: [{ id: 'r1', simulationId: 'sim-1', reviewerId: 'u1', status: 'pending', decisionReason: null, createdAt: '', updatedAt: '' }],
          approvals: [],
        }}
      />,
    )
    expect(screen.getByText(/waiting for a review decision/i)).toBeInTheDocument()
  })

  it('shows disabled permission button with tooltip reason', () => {
    render(
      <PermissionActionButton allowed={false} disabledReason="Not allowed">
        Approve
      </PermissionActionButton>,
    )
    expect(screen.getByRole('button', { name: 'Approve' })).toBeDisabled()
  })

  it('requires rejection and change-request reasons', async () => {
    const user = userEvent.setup()
    const onConfirm = vi.fn()
    render(
      <ReviewDecisionDialog
        open
        onOpenChange={() => undefined}
        title="Reject simulation"
        description="Provide a reason."
        confirmLabel="Reject"
        requireReason
        onConfirm={onConfirm}
      />,
    )
    await user.click(screen.getByRole('button', { name: 'Reject' }))
    expect(onConfirm).not.toHaveBeenCalled()
    await user.type(screen.getByRole('textbox'), 'RTP is outside tolerance')
    await user.click(screen.getByRole('button', { name: 'Reject' }))
    expect(onConfirm).toHaveBeenCalledWith('RTP is outside tolerance')
  })

  it('renders role-aware review panel and review decisions', () => {
    renderWithQuery(<SimulationReviewPanel simulationId="sim-1" />)
    expect(screen.getByText(/review actions/i)).toBeInTheDocument()
    expect(screen.getByText('admin')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /reject/i })).toBeInTheDocument()

    render(<ReviewDecisionsPanel reviews={[{
      id: 'review-1',
      simulationId: 'sim-1',
      reviewerId: 'user-2',
      reviewerName: 'Reviewer',
      reviewerEmail: 'reviewer@example.com',
      reviewerRole: 'admin',
      status: 'changes_requested',
      decisionReason: 'Lower scatter frequency',
      createdAt: '2026-01-01T00:00:00Z',
      updatedAt: '2026-01-01T00:00:00Z',
    }]} />)
    expect(screen.getByText(/lower scatter frequency/i)).toBeInTheDocument()
    expect(screen.getAllByText('admin').length).toBeGreaterThan(0)
  })

  it('renders comment author metadata', () => {
    renderWithQuery(<CommentsPanel simulationId="sim-1" />)
    expect(screen.getByText('Alice')).toBeInTheDocument()
    expect(screen.getByText(/please review scatter frequency/i)).toBeInTheDocument()
  })

  it('renders my pending reviews widget actions', () => {
    renderWithQuery(
      <MyPendingReviewsWidget
        items={[
          {
            simulationId: 'sim-review-1',
            workflowStatus: 'under_review',
            gameVersionId: 'version-1',
            updatedAt: '2026-01-03T00:00:00Z',
          },
        ]}
      />,
    )
    expect(screen.getByText(/my pending reviews/i)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Review' })).toHaveAttribute(
      'href',
      '/simulations/sim-review-1/review',
    )
    expect(screen.getByRole('link', { name: 'Approve' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Request Changes' })).toBeInTheDocument()
  })

  it('renders approval timeline and activity history', () => {
    render(
      <ApprovalTimeline
        approvals={[
          {
            id: 'a-1',
            simulationId: 'sim-1',
            approvedBy: 'user-1',
            approvalStage: 'mathematician',
            approvedAt: '2026-01-01T00:00:00Z',
          },
        ]}
      />,
    )
    expect(screen.getByText('Mathematician')).toBeInTheDocument()
    renderWithQuery(<ActivityTimeline simulationId="sim-1" />)
    expect(screen.getByText(/review approved/i)).toBeInTheDocument()
  })

  it('renders empty review decisions and enabled permission button', async () => {
    const user = userEvent.setup()
    const onClick = vi.fn()
    render(<ReviewDecisionsPanel reviews={[]} />)
    expect(screen.getByText(/no review decisions yet/i)).toBeInTheDocument()
    render(
      <PermissionActionButton allowed onClick={onClick}>
        Approve
      </PermissionActionButton>,
    )
    await user.click(screen.getByRole('button', { name: 'Approve' }))
    expect(onClick).toHaveBeenCalled()
  })

  it('opens review dialogs from panel actions', async () => {
    const user = userEvent.setup()
    renderWithQuery(<SimulationReviewPanel simulationId="sim-1" />)
    await user.click(screen.getByRole('button', { name: /request changes/i }))
    expect(screen.getByText(/send the simulation back to draft/i)).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Cancel' }))
    await user.click(screen.getByRole('button', { name: 'Reject' }))
    expect(screen.getByText(/reject the mathematics review/i)).toBeInTheDocument()
  })

  it('renders workflow-specific actions for each status', () => {
    workflowState.status = 'draft'
    renderWithQuery(<SimulationReviewPanel simulationId="sim-1" />)
    expect(screen.getByRole('button', { name: /request review/i })).toBeInTheDocument()

    workflowState.status = 'approved'
    renderWithQuery(<SimulationReviewPanel simulationId="sim-1" />)
    expect(screen.getByRole('button', { name: /mark certification ready/i })).toBeInTheDocument()

    workflowState.status = 'certification_ready'
    workflowState.role = 'owner'
    renderWithQuery(<SimulationReviewPanel simulationId="sim-1" />)
    expect(screen.getByRole('button', { name: /release simulation/i })).toBeInTheDocument()
  })

  it('confirms review and stage approval dialogs', async () => {
    const user = userEvent.setup()
    workflowState.status = 'under_review'
    renderWithQuery(<SimulationReviewPanel simulationId="sim-1" />)
    await user.click(screen.getByRole('button', { name: /approve mathematics/i }))
    await user.click(screen.getByRole('button', { name: 'Approve' }))
    expect(submitReviewMutate).toHaveBeenCalled()

    await user.click(screen.getByRole('button', { name: /request changes/i }))
    await user.type(screen.getByRole('textbox'), 'Adjust scatter weights')
    await user.click(screen.getByRole('button', { name: /request changes/i }))
    expect(submitReviewMutate).toHaveBeenCalled()

    workflowState.status = 'approved'
    workflowState.approvals = []
    renderWithQuery(<SimulationReviewPanel simulationId="sim-1" />)
    await user.click(screen.getByRole('button', { name: /record mathematician approval/i }))
    await user.click(screen.getByRole('button', { name: /approve stage/i }))
    expect(approveMutate).toHaveBeenCalled()
  })

  it('submits remaining stage approval dialogs', async () => {
    const user = userEvent.setup()
    workflowState.status = 'approved'
    workflowState.approvals = [
      {
        id: 'a-1',
        simulationId: 'sim-1',
        approvedBy: 'user-1',
        approvalStage: 'mathematician',
        approvedAt: '2026-01-01T00:00:00Z',
      },
    ]
    renderWithQuery(<SimulationReviewPanel simulationId="sim-1" />)
    await user.click(screen.getByRole('button', { name: /record senior mathematician approval/i }))
    await user.click(screen.getByRole('button', { name: /approve stage/i }))
    expect(approveMutate).toHaveBeenCalled()
  })

  it('adds collaboration comments when permitted', async () => {
    const user = userEvent.setup()
    renderWithQuery(<CommentsPanel simulationId="sim-1" />)
    await user.type(screen.getByRole('textbox'), 'Needs another review pass')
    await user.click(screen.getByRole('button', { name: /add comment/i }))
    expect(addCommentMutate).toHaveBeenCalled()
  })

  it('shows disabled actions for viewers on draft simulations', () => {
    workflowState.status = 'draft'
    workflowState.role = 'viewer'
    renderWithQuery(<SimulationReviewPanel simulationId="sim-1" />)
    expect(screen.getByRole('button', { name: /request review/i })).toBeDisabled()
  })

  it('invokes next action callback', async () => {
    const user = userEvent.setup()
    const onAction = vi.fn()
    render(
      <ReviewNextActionCard
        workflow={{
          simulationId: 'sim-1',
          status: 'under_review',
          reviews: [],
          approvals: [],
        }}
        role="admin"
        onAction={onAction}
      />,
    )
    await user.click(screen.getByRole('button', { name: /approve mathematics/i }))
    expect(onAction).toHaveBeenCalledWith('approve')
  })

  it('covers activity loading and pending notice edge cases', () => {
    vi.mocked(useSimulationActivity).mockReturnValueOnce({
      data: { items: [] },
      isLoading: true,
    } as never)
    renderWithQuery(<ActivityTimeline simulationId="sim-1" />)
    expect(screen.getByText(/loading activity/i)).toBeInTheDocument()

    const { container } = render(
      <PendingApprovalsNotice
        workflow={{
          simulationId: 'sim-1',
          status: 'released',
          reviews: [],
          approvals: [],
        }}
      />,
    )
    expect(container).toBeEmptyDOMElement()
  })

  it('shows developer messaging in my pending reviews widget', () => {
    workflowState.role = 'developer'
    renderWithQuery(<MyPendingReviewsWidget items={[]} />)
    expect(screen.getByText(/admins and owners/i)).toBeInTheDocument()
  })

  it('opens producer approval dialog', async () => {
    const user = userEvent.setup()
    workflowState.status = 'approved'
    workflowState.approvals = [
      { id: 'a1', simulationId: 'sim-1', approvedBy: 'u', approvalStage: 'mathematician', approvedAt: '' },
      { id: 'a2', simulationId: 'sim-1', approvedBy: 'u', approvalStage: 'senior_mathematician', approvedAt: '' },
      { id: 'a3', simulationId: 'sim-1', approvedBy: 'u', approvalStage: 'product_owner', approvedAt: '' },
    ]
    workflowState.role = 'owner'
    renderWithQuery(<SimulationReviewPanel simulationId="sim-1" />)
    await user.click(screen.getByRole('button', { name: /record producer approval/i }))
    await user.click(screen.getByRole('button', { name: /approve stage/i }))
    expect(approveMutate).toHaveBeenCalled()
  })

  it('requests review from draft and opens initial reject dialog', async () => {
    const user = userEvent.setup()
    workflowState.status = 'draft'
    renderWithQuery(<SimulationReviewPanel simulationId="sim-1" />)
    await user.click(screen.getByRole('button', { name: /request review/i }))
    expect(transitionMutate).toHaveBeenCalledWith('under_review')

    renderWithQuery(<SimulationReviewPanel simulationId="sim-1" initialDialog="reject" />)
    await user.type(screen.getByRole('textbox'), 'RTP out of tolerance')
    await user.click(screen.getByRole('button', { name: 'Reject' }))
    expect(submitReviewMutate).toHaveBeenCalled()
  })

  it('renders widget loading state and empty activity list', () => {
    renderWithQuery(<MyPendingReviewsWidget loading />)
    expect(document.querySelectorAll('.animate-pulse').length).toBeGreaterThan(0)

    vi.mocked(useSimulationActivity).mockReturnValueOnce({
      data: { items: [] },
      isLoading: false,
    } as never)
    renderWithQuery(<ActivityTimeline simulationId="sim-1" />)
    expect(screen.getByText(/no activity yet/i)).toBeInTheDocument()
  })

  it('opens product owner approval dialog', async () => {
    const user = userEvent.setup()
    workflowState.status = 'approved'
    workflowState.approvals = [
      { id: 'a1', simulationId: 'sim-1', approvedBy: 'u', approvalStage: 'mathematician', approvedAt: '' },
      { id: 'a2', simulationId: 'sim-1', approvedBy: 'u', approvalStage: 'senior_mathematician', approvedAt: '' },
    ]
    renderWithQuery(<SimulationReviewPanel simulationId="sim-1" />)
    await user.click(screen.getByRole('button', { name: /record product owner approval/i }))
    await user.click(screen.getByRole('button', { name: /approve stage/i }))
    expect(approveMutate).toHaveBeenCalled()
  })
})
