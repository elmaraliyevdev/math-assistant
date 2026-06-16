import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'

import { ErrorBoundary } from '@/components/error-boundary'

function Broken(): never {
  throw new Error('Boom')
}

describe('ErrorBoundary', () => {
  it('renders fallback UI on error', () => {
    render(
      <ErrorBoundary>
        <Broken />
      </ErrorBoundary>,
    )

    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument()
    expect(screen.getByText('Boom')).toBeInTheDocument()
  })
})
