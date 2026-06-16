import { MetricsCards } from '@/features/simulations/components/MetricsCards'
import { GlossaryTerm } from '@/components/glossary-term'
import type { SimulationResults } from '@/types/api'
import { formatNumber, formatPercent } from '@/lib/utils'

interface VolatilityDashboardProps {
  results: SimulationResults
  spinCount: number
}

export function VolatilityDashboard({
  results,
  spinCount,
}: VolatilityDashboardProps) {
  const { volatilityMetrics, hitFrequency } = results

  return (
    <MetricsCards
      title={<GlossaryTerm term="volatility">Volatility metrics</GlossaryTerm>}
      metrics={[
        {
          label: 'Standard deviation',
          value: volatilityMetrics.standardDeviation.toFixed(4),
        },
        {
          label: 'Coefficient of variation',
          value:
            volatilityMetrics.coefficientOfVariation == null
              ? '—'
              : volatilityMetrics.coefficientOfVariation.toFixed(4),
        },
        {
          label: 'Mean win (minor units)',
          value: volatilityMetrics.meanWinMinorUnits.toFixed(4),
        },
        {
          label: 'Hit frequency',
          value: formatPercent(results.summary.hitFrequency),
          glossaryTerm: 'hitFrequency',
        },
        {
          label: 'Winning spins',
          value: formatNumber(hitFrequency.winningSpinCount),
        },
        {
          label: 'Total spins',
          value: formatNumber(spinCount),
        },
      ]}
    />
  )
}
