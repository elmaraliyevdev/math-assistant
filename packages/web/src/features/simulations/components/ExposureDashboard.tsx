import type { SimulationResults } from '@/types/api'
import { MetricsCards } from '@/features/simulations/components/MetricsCards'
import { formatNumber, formatPercent } from '@/lib/utils'

interface ExposureDashboardProps {
  results: SimulationResults
}

export function ExposureDashboard({ results }: ExposureDashboardProps) {
  const { exposure } = results

  return (
    <MetricsCards
      title="Exposure metrics"
      metrics={[
        {
          label: 'Truncation rate',
          value: formatPercent(exposure.truncationRate),
        },
        {
          label: 'Exposure cap applied',
          value: exposure.exposureCapApplied ? 'Yes' : 'No',
          glossaryTerm: 'exposureCap',
        },
        {
          label: 'Truncated wins',
          value: formatNumber(exposure.totalTruncatedMinorUnits),
        },
        { label: 'Capped RTP', value: formatPercent(exposure.cappedRtp) },
        { label: 'Uncapped RTP', value: formatPercent(exposure.uncappedRtp) },
      ]}
    />
  )
}
