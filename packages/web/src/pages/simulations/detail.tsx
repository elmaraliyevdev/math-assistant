import { useParams } from '@tanstack/react-router'
import { RefreshCw } from 'lucide-react'
import { Link } from '@tanstack/react-router'

import { Badge, statusBadgeVariant } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import {
  CertificationNotice,
  ConfidenceIntervalChart,
  ExposureDashboard,
  FeatureFrequencyChart,
  FeatureValidationChart,
  JackpotFrequencyChart,
  MetricsCards,
  MathConfigurationSnapshot,
  RTPDashboard,
  RtpDecompositionPieChart,
  RtpTargetGauge,
  RtpValidationCard,
  SimulationNotesPanel,
  SimulationProgress,
  VolatilityDashboard,
  WinDistributionChart,
} from '@/features/simulations/components'
import { DistributedSimulationPanel } from '@/features/distributed/components/DistributedSimulationPanel'
import { SimulationExportMenu } from '@/features/exports/components/SimulationExportMenu'
import {
  useCancelSimulation,
  useSimulation,
  useSimulationResults,
} from '@/features/simulations/hooks/use-simulations'
import { useGameVersionBySimulation } from '@/features/simulations/hooks/use-game-version-lookup'
import { CalibrationDashboard } from '@/features/workbench/components/CalibrationDashboard'
import { TuningRecommendationsPanel } from '@/features/workbench/components/TuningRecommendationsPanel'
import { useSimulationCalibration } from '@/features/workbench/hooks/use-workbench'
import { formatDate, formatNumber, formatPercent } from '@/lib/utils'

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
      <div className="space-y-4">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-28 w-full" />
        <Skeleton className="h-48 w-full" />
      </div>
    )
  }

  if (simulation.isError || !simulation.data) {
    return (
      <div className="rounded-lg border border-destructive/40 bg-destructive/5 p-6">
        <p className="font-medium text-destructive">Simulation not found</p>
        <p className="mt-1 text-sm text-muted-foreground">
          The simulation may have been removed or you may not have access.
        </p>
      </div>
    )
  }

  const detail = simulation.data
  const canCancel =
    detail.status === 'pending' || detail.status === 'running'
  const showResults = detail.status === 'completed' && results.data

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-3">
            <h2 className="text-2xl font-bold tracking-tight">Simulation</h2>
            <Badge variant={statusBadgeVariant(detail.status)}>
              {detail.status}
            </Badge>
          </div>
          <p className="mt-1 font-mono text-sm text-muted-foreground">
            {detail.id}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {detail.status === 'completed' && (
            <>
              <Button variant="secondary" asChild>
                <Link
                  to="/simulations/compare"
                  search={{ ids: detail.id }}
                >
                  Compare
                </Link>
              </Button>
              <Button variant="outline" asChild>
                <Link
                  to="/mathematics"
                  search={{
                    gameVersionId: detail.gameVersionId,
                    simulationId: detail.id,
                  }}
                >
                  View mathematics
                </Link>
              </Button>
              <Button variant="secondary" asChild>
                <Link
                  to="/simulations/$simulationId/review"
                  params={{ simulationId: detail.id }}
                >
                  Review workflow
                </Link>
              </Button>
            </>
          )}
          {detail.status === 'completed' && (
            <SimulationExportMenu simulationId={detail.id} />
          )}
          <Button
            variant="outline"
            onClick={() => {
              simulation.refetch()
              if (detail.status === 'completed') {
                results.refetch()
              }
            }}
            disabled={simulation.isFetching}
          >
            <RefreshCw
              className={`h-4 w-4 ${simulation.isFetching ? 'animate-spin' : ''}`}
            />
            Refresh results
          </Button>
          {canCancel && (
            <Button
              variant="destructive"
              onClick={() => cancelSimulation.mutate()}
              disabled={cancelSimulation.isPending}
            >
              Cancel simulation
            </Button>
          )}
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Metadata</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 text-sm sm:grid-cols-2 lg:grid-cols-3">
          <MetadataItem label="Simulation ID" value={detail.id} mono />
          <MetadataItem label="Status" value={detail.status} />
          <MetadataItem label="Created at" value={formatDate(detail.createdAt)} />
          <MetadataItem
            label="Started at"
            value={formatDate(detail.startedAt)}
          />
          <MetadataItem
            label="Completed at"
            value={formatDate(detail.completedAt)}
          />
          <MetadataItem label="Worker ID" value={detail.workerId ?? '—'} mono />
          <MetadataItem
            label="Spin count"
            value={formatNumber(detail.spinCount)}
          />
          <MetadataItem
            label="Bet (minor units)"
            value={formatNumber(detail.betMinorUnits)}
          />
          <MetadataItem label="Event log mode" value={detail.eventLogMode} />
        </CardContent>
      </Card>

      <SimulationProgress
        progress={detail.progress}
        spinCount={detail.spinCount}
        errorMessage={detail.errorMessage}
      />

      <DistributedSimulationPanel
        simulationId={detail.id}
        distributedExecution={Boolean(detail.distributedExecution)}
        enabled={detail.status === 'running' || detail.status === 'completed'}
      />

      {detail.status === 'completed' && results.isLoading && (
        <Skeleton className="h-64 w-full" />
      )}

      {detail.status === 'completed' && results.isError && (
        <div className="rounded-lg border border-dashed p-6 text-center text-sm text-muted-foreground">
          Results are not available yet. Try refreshing in a moment.
        </div>
      )}

      {showResults && (
        <div className="space-y-8">
          <CertificationNotice notice={results.data.certificationNotice} />
          <CalibrationDashboard
            data={calibration.data}
            isLoading={calibration.isLoading}
            error={
              calibration.isError ? 'Unable to load calibration comparison.' : null
            }
          />
          <RTPDashboard results={results.data} />
          {results.data.rtpValidation && (
            <>
              <RtpValidationCard validation={results.data.rtpValidation} />
              <RtpTargetGauge validation={results.data.rtpValidation} />
            </>
          )}
          <TuningRecommendationsPanel
            simulationId={detail.id}
            recommendations={results.data.recommendations}
          />
          {gameVersion.data?.canonicalJson && (
            <MathConfigurationSnapshot
              canonicalJson={gameVersion.data.canonicalJson}
            />
          )}
          {detail.status === 'completed' && (
            <SimulationNotesPanel simulationId={detail.id} />
          )}
          <div className="grid gap-6 xl:grid-cols-2">
            <RtpDecompositionPieChart chart={results.data.rtpDecompositionChart} />
            <FeatureValidationChart items={results.data.featureValidation} />
          </div>
          <MetricsCards
            title="Hit metrics"
            metrics={[
              {
                label: 'Hit frequency',
                value: formatPercent(results.data.summary.hitFrequency),
              },
              {
                label: 'Winning spins',
                value: formatNumber(results.data.hitFrequency.winningSpinCount),
              },
              {
                label: 'Total bet',
                value: formatNumber(results.data.totals.totalBetMinorUnits),
              },
              {
                label: 'Total win',
                value: formatNumber(results.data.totals.totalWinMinorUnits),
              },
            ]}
          />
          <ExposureDashboard results={results.data} />
          <VolatilityDashboard
            results={results.data}
            spinCount={detail.spinCount}
          />
          <MetricsCards
            title="Confidence metrics"
            metrics={[
              {
                label: 'RTP CI lower',
                value: formatPercent(results.data.confidenceInterval.lowerBound),
              },
              {
                label: 'RTP CI upper',
                value: formatPercent(results.data.confidenceInterval.upperBound),
              },
              {
                label: 'Confidence level',
                value: formatPercent(
                  results.data.confidenceInterval.confidenceLevel,
                  0,
                ),
              },
            ]}
          />

          <div className="grid gap-6 xl:grid-cols-2">
            <WinDistributionChart distribution={results.data.winDistribution} />
            <ConfidenceIntervalChart interval={results.data.confidenceInterval} />
            <FeatureFrequencyChart features={results.data.featureFrequencies} />
            <JackpotFrequencyChart jackpots={results.data.jackpotFrequencies} />
          </div>

          <FeatureMetricsTable features={results.data.featureFrequencies} />
          <JackpotMetricsTable jackpots={results.data.jackpotFrequencies} />
        </div>
      )}
    </div>
  )
}

function MetadataItem({
  label,
  value,
  mono = false,
}: {
  label: string
  value: string
  mono?: boolean
}) {
  return (
    <div>
      <p className="text-muted-foreground">{label}</p>
      <p className={mono ? 'font-mono text-xs break-all' : 'font-medium'}>
        {value}
      </p>
    </div>
  )
}

function FeatureMetricsTable({
  features,
}: {
  features: Array<{
    featureName: string
    triggerCount: number
    frequency: number
    oneInX: number | null
  }>
}) {
  if (features.length === 0) return null

  return (
    <Card>
      <CardHeader>
        <CardTitle>Feature metrics</CardTitle>
      </CardHeader>
      <CardContent className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-muted-foreground">
              <th className="pb-2 pr-4 font-medium">Feature</th>
              <th className="pb-2 pr-4 font-medium">Triggers</th>
              <th className="pb-2 pr-4 font-medium">Frequency</th>
              <th className="pb-2 font-medium">One in X</th>
            </tr>
          </thead>
          <tbody>
            {features.map((feature) => (
              <tr key={feature.featureName} className="border-b last:border-0">
                <td className="py-2 pr-4">{feature.featureName}</td>
                <td className="py-2 pr-4">{formatNumber(feature.triggerCount)}</td>
                <td className="py-2 pr-4">{formatPercent(feature.frequency)}</td>
                <td className="py-2">
                  {feature.oneInX != null ? feature.oneInX.toFixed(1) : '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardContent>
    </Card>
  )
}

function JackpotMetricsTable({
  jackpots,
}: {
  jackpots: Array<{
    jackpotTier: string
    triggerCount: number
    frequency: number
    oneInX: number | null
  }>
}) {
  if (jackpots.length === 0) return null

  return (
    <Card>
      <CardHeader>
        <CardTitle>Jackpot metrics</CardTitle>
      </CardHeader>
      <CardContent className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-muted-foreground">
              <th className="pb-2 pr-4 font-medium">Tier</th>
              <th className="pb-2 pr-4 font-medium">Hits</th>
              <th className="pb-2 pr-4 font-medium">Frequency</th>
              <th className="pb-2 font-medium">One in X</th>
            </tr>
          </thead>
          <tbody>
            {jackpots.map((jackpot) => (
              <tr key={jackpot.jackpotTier} className="border-b last:border-0">
                <td className="py-2 pr-4">{jackpot.jackpotTier}</td>
                <td className="py-2 pr-4">{formatNumber(jackpot.triggerCount)}</td>
                <td className="py-2 pr-4">{formatPercent(jackpot.frequency)}</td>
                <td className="py-2">
                  {jackpot.oneInX != null ? jackpot.oneInX.toFixed(1) : '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardContent>
    </Card>
  )
}
