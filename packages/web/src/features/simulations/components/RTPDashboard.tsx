import { MetricsCards } from '@/features/simulations/components/MetricsCards'
import type { SimulationResults } from '@/types/api'
import { formatPercent } from '@/lib/utils'

interface RTPDashboardProps {
  results: SimulationResults
}

export function RTPDashboard({ results }: RTPDashboardProps) {
  const { summary, exposure } = results

  return (
    <MetricsCards
      title="RTP metrics"
      metrics={[
        { label: 'RTP', value: formatPercent(summary.rtp), glossaryTerm: 'rtp' },
        { label: 'Uncapped RTP', value: formatPercent(summary.uncappedRtp) },
        {
          label: 'RTP difference',
          value: formatPercent(exposure.rtpDifference),
        },
      ]}
    />
  )
}
