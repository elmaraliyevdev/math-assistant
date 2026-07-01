import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { CitationPanel } from '@/features/assistant/components/CitationPanel'
import type { GroundedCitation } from '@/types/api'

const citations: GroundedCitation[] = [
  {
    label: 'Simulation #123',
    source: 'simulation_results',
    path: 'mathematics_report.rtpDecompositionChart.FREE_SPINS',
    value: 45.7,
  },
  {
    label: 'Calibration Report',
    source: 'calibration_report',
    path: 'recommendations.paytable',
  },
]

describe('Assistant components', () => {
  it('renders grounded citations', () => {
    render(<CitationPanel citations={citations} />)
    expect(screen.getByText('Citations')).toBeInTheDocument()
    expect(screen.getByText('Simulation #123')).toBeInTheDocument()
    expect(
      screen.getByText(
        'simulation_results.mathematics_report.rtpDecompositionChart.FREE_SPINS = 45.7',
      ),
    ).toBeInTheDocument()
    expect(screen.getByText('Calibration Report')).toBeInTheDocument()
  })

  it('renders nothing when citations are empty', () => {
    const { container } = render(<CitationPanel citations={[]} />)
    expect(container).toBeEmptyDOMElement()
  })
})
