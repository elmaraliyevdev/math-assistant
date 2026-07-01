import { useParams } from '@tanstack/react-router'

import { PageLayout, PageSection } from '@/components/design-system'
import { Skeleton } from '@/components/ui/skeleton'
import { SimulationAdvancedSection } from '@/features/simulations/components/detail/SimulationAdvancedSection'
import { SimulationChartsDashboard } from '@/features/simulations/components/detail/SimulationChartsDashboard'
import { SimulationDesignComparison } from '@/features/simulations/components/detail/SimulationDesignComparison'
import { SimulationDetailHero } from '@/features/simulations/components/detail/SimulationDetailHero'
import { SimulationHealthSummary } from '@/features/simulations/components/detail/SimulationHealthSummary'
import { SimulationMetricsTabs } from '@/features/simulations/components/detail/SimulationMetricsTabs'
import { SimulationRecommendationsTimeline } from '@/features/simulations/components/detail/SimulationRecommendationsTimeline'
import { SimulationTopInsights } from '@/features/simulations/components/detail/SimulationTopInsights'
import {
  useCancelSimulation,
  useSimulation,
  useSimulationResults,
} from '@/features/simulations/hooks/use-simulations'
import { useGameVersionBySimulation } from '@/features/simulations/hooks/use-game-version-lookup'
import { useSimulationCalibration } from '@/features/workbench/hooks/use-workbench'

export function SimulationDetailPage() {
  const { simulationId } = useParams({ strict: false }) as {
    simulationId: string
  }
  const simulation = useSimulation(simulationId, true)
  const results = useSimulationResults(
    simulationId,
    simulation.data?.status === 'completed',
  )
  const cancelSimulation = useCancelSimulation(simulationId)
  const gameVersion = useGameVersionBySimulation(simulation.data?.gameVersionId)
  const calibration = useSimulationCalibration(
    simulation.data?.gameVersionId,
    simulationId,
    simulation.data?.status === 'completed',
  )

  if (simulation.isLoading) {
    return (
      <PageLayout>
        <div className="space-y-4">
          <Skeleton className="h-24 w-full rounded-xl" />
          <Skeleton className="h-40 w-full rounded-xl" />
          <Skeleton className="h-64 w-full rounded-xl" />
        </div>
      </PageLayout>
    )
  }

  if (simulation.isError || !simulation.data) {
    return (
      <PageLayout>
        <div className="rounded-xl border border-destructive/30 bg-destructive/5 p-8">
          <p className="font-medium text-destructive">Simulation not found</p>
          <p className="mt-1 text-sm text-muted-foreground">
            The simulation may have been removed or you may not have access.
          </p>
        </div>
      </PageLayout>
    )
  }

  const detail = simulation.data
  const showResults = detail.status === 'completed' && results.data

  return (
    <PageLayout>
      <PageSection className="space-y-8">
        <SimulationDetailHero
          detail={detail}
          gameName={gameVersion.gameName}
          versionNumber={gameVersion.versionNumber}
          onRefresh={() => {
            simulation.refetch()
            if (detail.status === 'completed') results.refetch()
          }}
          refreshing={simulation.isFetching}
          onCancel={() => cancelSimulation.mutate()}
          cancelling={cancelSimulation.isPending}
        />

        {detail.status === 'completed' && results.isLoading && (
          <Skeleton className="h-64 w-full rounded-xl" />
        )}

        {detail.status === 'completed' && results.isError && (
          <div className="rounded-xl border border-dashed border-border/60 p-8 text-center text-sm text-muted-foreground">
            Results are not available yet. Try refreshing in a moment.
          </div>
        )}

        {showResults && (
          <>
            <SimulationHealthSummary results={results.data} />
            <SimulationTopInsights
              results={results.data}
              intelligence={results.data.simulationIntelligence}
            />
            <SimulationDesignComparison
              results={results.data}
              intelligence={results.data.simulationIntelligence}
            />
            <SimulationRecommendationsTimeline
              simulationId={detail.id}
              recommendations={results.data.recommendations}
              intelligence={results.data.simulationIntelligence}
            />
            <SimulationChartsDashboard results={results.data} />
            <SimulationMetricsTabs
              results={results.data}
              spinCount={detail.spinCount}
            />
            <SimulationAdvancedSection
              detail={detail}
              results={results.data}
              calibration={calibration.data}
              calibrationLoading={calibration.isLoading}
              calibrationError={
                calibration.isError ? 'Unable to load calibration comparison.' : null
              }
              canonicalJson={gameVersion.data?.canonicalJson}
            />
          </>
        )}
      </PageSection>
    </PageLayout>
  )
}
