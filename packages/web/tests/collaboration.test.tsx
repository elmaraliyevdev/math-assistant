import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { WorkflowStatusCard } from '@/features/collaboration/components/WorkflowStatusCard'

vi.mock('@tanstack/react-router', () => ({
  Link: ({ children }: { children: React.ReactNode }) => <a>{children}</a>,
  useParams: () => ({ simulationId: 'sim-1' }),
}))

describe('WorkflowStatusCard', () => {
  it('renders workflow steps with current status', () => {
    render(<WorkflowStatusCard status="under_review" />)
    expect(screen.getByText('Under Review')).toBeInTheDocument()
    expect(screen.getByText('Draft')).toBeInTheDocument()
    expect(screen.getByText('Released')).toBeInTheDocument()
  })
})

describe('Simulation review page building blocks', () => {
  it('wraps collaboration components in query client', () => {
    const client = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    })
    render(
      <QueryClientProvider client={client}>
        <WorkflowStatusCard status="approved" />
      </QueryClientProvider>,
    )
    expect(screen.getByText('Approved')).toBeInTheDocument()
  })
})
