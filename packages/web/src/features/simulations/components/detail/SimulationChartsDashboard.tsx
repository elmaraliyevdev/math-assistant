import {
  ConfidenceIntervalChart,
  FeatureFrequencyChart,
  FeatureValidationChart,
  JackpotFrequencyChart,
  RtpDecompositionPieChart,
  WinDistributionChart,
} from '@/features/simulations/components'
import type { SimulationResults } from '@/types/api'

export function SimulationChartsDashboard({
  results,
}: {
  results: SimulationResults
}) {
  return (
    <section className="space-y-4">
      <div>
        <h2 className="text-lg font-medium">Distribution & charts</h2>
        <p className="text-sm text-muted-foreground">
          RTP decomposition, win distribution, volatility, and feature frequency.
        </p>
      </div>
      <div className="grid gap-4 xl:grid-cols-2">
        <RtpDecompositionPieChart chart={results.rtpDecompositionChart} />
        <FeatureValidationChart items={results.featureValidation} />
        <WinDistributionChart distribution={results.winDistribution} />
        <ConfidenceIntervalChart interval={results.confidenceInterval} />
        <FeatureFrequencyChart features={results.featureFrequencies} />
        <JackpotFrequencyChart jackpots={results.jackpotFrequencies} />
      </div>
    </section>
  )
}
