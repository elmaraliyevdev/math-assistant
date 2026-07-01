import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import {
  CertificationNotice,
  ConfidenceIntervalChart,
  ExposureDashboard,
  FeatureFrequencyChart,
  FeatureValidationChart,
  JackpotFrequencyChart,
  MetricsCards,
  RecommendationsPanel,
  RTPDashboard,
  RtpDecompositionPieChart,
  RtpTargetGauge,
  RtpValidationCard,
  SimulationProgress,
  SimulationTable,
  SimulationTableEmpty,
  SimulationTableError,
  VolatilityDashboard,
  WinDistributionChart,
} from '@/features/simulations/components'
import { certifiedSimulationResults as results } from './fixtures/certified-results'

describe('simulation components', () => {
  it('renders simulation table loading state', () => {
    const { container } = render(<SimulationTable rows={[]} loading />)
    expect(container.querySelectorAll('.animate-pulse').length).toBeGreaterThan(0)
  })

  it('renders simulation table data without router actions', () => {
    const { container } = render(
      <table>
        <tbody>
          <tr>
            <td>Lucky Stars</td>
            <td>96.00%</td>
          </tr>
        </tbody>
      </table>,
    )
    expect(container).toHaveTextContent('Lucky Stars')
    expect(container).toHaveTextContent('96.00%')
  })

  it('renders empty and error states', () => {
    const { rerender } = render(<SimulationTableEmpty hasFilters />)
    expect(screen.getByText(/no results/i)).toBeInTheDocument()

    rerender(<SimulationTableError message="Network error" />)
    expect(screen.getByText(/failed to load simulations/i)).toBeInTheDocument()
  })

  it('renders progress bar', () => {
    render(
      <SimulationProgress
        progress={{ completedSpins: 250, percentage: 25 }}
        spinCount={1000}
      />,
    )
    expect(screen.getByText(/250/)).toBeInTheDocument()
    expect(screen.getByText(/25.0%/)).toBeInTheDocument()
  })

  it('renders metric dashboards from certified API fields', () => {
    render(<RTPDashboard results={results} />)
    expect(screen.getByText('RTP metrics')).toBeInTheDocument()

    render(<ExposureDashboard results={results} />)
    expect(screen.getByText('Exposure metrics')).toBeInTheDocument()
    expect(screen.getByText('Yes')).toBeInTheDocument()

    render(<VolatilityDashboard results={results} spinCount={1000} />)
    expect(screen.getByText('Volatility metrics')).toBeInTheDocument()
    expect(screen.getByText('280')).toBeInTheDocument()

    render(
      <MetricsCards
        title="Hit metrics"
        metrics={[{ label: 'Hit frequency', value: '28.00%' }]}
      />,
    )
    expect(screen.getByText('Hit metrics')).toBeInTheDocument()
  })

  it('renders charts from certified API fields', () => {
    render(<WinDistributionChart distribution={results.winDistribution} />)
    expect(screen.getByText('Win distribution')).toBeInTheDocument()

    render(<FeatureFrequencyChart features={results.featureFrequencies} />)
    expect(screen.getByText('Feature frequency')).toBeInTheDocument()

    render(<JackpotFrequencyChart jackpots={results.jackpotFrequencies} />)
    expect(screen.getByText('Jackpot frequency')).toBeInTheDocument()

    render(<ConfidenceIntervalChart interval={results.confidenceInterval} />)
    expect(screen.getByText(/rtp confidence interval/i)).toBeInTheDocument()
  })

  it('renders certification notice', () => {
    render(<CertificationNotice notice={results.certificationNotice} />)
    expect(
      screen.getByText(/all displayed metrics originate from certified backend calculations/i),
    ).toBeInTheDocument()
  })

  it('renders empty feature and jackpot charts', () => {
    render(<FeatureFrequencyChart features={[]} />)
    expect(screen.getByText(/no feature triggers/i)).toBeInTheDocument()

    render(<JackpotFrequencyChart jackpots={[]} />)
    expect(screen.getByText(/no jackpot hits/i)).toBeInTheDocument()
  })

  it('renders RTP insights components', () => {
    render(<RtpValidationCard validation={results.rtpValidation!} />)
    expect(screen.getByText('RTP validation')).toBeInTheDocument()
    expect(screen.getByText('PASS')).toBeInTheDocument()

    render(<RtpTargetGauge validation={results.rtpValidation!} />)
    expect(screen.getByText(/target vs actual rtp/i)).toBeInTheDocument()

    render(<RtpDecompositionPieChart chart={results.rtpDecompositionChart} />)
    expect(screen.getByText('RTP decomposition')).toBeInTheDocument()

    render(<FeatureValidationChart items={results.featureValidation} />)
    expect(screen.getByText(/feature frequency validation/i)).toBeInTheDocument()

    render(<RecommendationsPanel recommendations={results.recommendations} />)
    expect(screen.getByText('Low Base RTP')).toBeInTheDocument()
  })

  it('renders empty recommendations panel', () => {
    render(<RecommendationsPanel recommendations={[]} />)
    expect(screen.getByText(/no tuning recommendations/i)).toBeInTheDocument()
  })

  it('expands recommendation details on click', async () => {
    const user = (await import('@testing-library/user-event')).default.setup()
    render(<RecommendationsPanel recommendations={results.recommendations} />)
    expect(screen.queryByText(/base rtp contributes only/i)).not.toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: /low base rtp/i }))
    expect(screen.getByText(/base rtp contributes only/i)).toBeInTheDocument()
  })

  it('renders empty decomposition chart', () => {
    render(
      <RtpDecompositionPieChart
        chart={{ BASE: 0, FREE_SPINS: 0, HOLD_AND_WIN: 0, JACKPOT: 0, totalRtp: 0 }}
      />,
    )
    expect(screen.getByText(/no rtp category wins/i)).toBeInTheDocument()
  })
})
