import { Link } from '@tanstack/react-router'
import { RefreshCw } from 'lucide-react'

import { ActionBar } from '@/components/design-system/page-layout'
import { Button } from '@/components/ui/button'
import { SimulationExportMenu } from '@/features/exports/components/SimulationExportMenu'
import { SimulationProgress } from '@/features/simulations/components/SimulationProgress'
import { SimulationStatusBadge } from '@/features/simulations/components/SimulationStatusBadge'
import { formatDurationMs } from '@/features/simulations/utils/workbench'
import { simulationDurationMs } from '@/features/simulations/utils/health-score'
import type { SimulationDetail } from '@/types/api'
import { formatDate, formatNumber } from '@/lib/utils'

export function SimulationDetailHero({
  detail,
  gameName,
  versionNumber,
  onRefresh,
  refreshing,
  onCancel,
  cancelling,
  previewMode = false,
}: {
  detail: SimulationDetail
  gameName?: string
  versionNumber?: number | null
  onRefresh?: () => void
  refreshing?: boolean
  onCancel?: () => void
  cancelling?: boolean
  previewMode?: boolean
}) {
  const duration = simulationDurationMs(detail.createdAt, detail.completedAt)
  const canCancel = detail.status === 'pending' || detail.status === 'running'

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-semibold tracking-tight">Simulation</h1>
            <SimulationStatusBadge status={detail.status} />
          </div>
          <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-muted-foreground">
            <span className="font-mono text-xs text-foreground/80">{detail.id}</span>
            {gameName ? (
              <span>
                {gameName}
                {versionNumber != null ? ` · v${versionNumber}` : ''}
              </span>
            ) : null}
            <span>{formatNumber(detail.spinCount)} spins</span>
            <span>Duration {formatDurationMs(duration)}</span>
            <span>Started {formatDate(detail.startedAt)}</span>
            <span>Completed {formatDate(detail.completedAt)}</span>
          </div>
        </div>
        <ActionBar className="flex-wrap">
          {!previewMode && detail.status === 'completed' && (
            <>
              <Button variant="outline" size="sm" asChild>
                <Link to="/simulations/compare" search={{ ids: detail.id }}>
                  Compare
                </Link>
              </Button>
              <SimulationExportMenu simulationId={detail.id} />
            </>
          )}
          {!previewMode && onRefresh ? (
            <Button
              variant="outline"
              size="sm"
              onClick={onRefresh}
              disabled={refreshing}
            >
              <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          ) : null}
          {!previewMode && canCancel && onCancel ? (
            <Button
              variant="destructive"
              size="sm"
              onClick={onCancel}
              disabled={cancelling}
            >
              Cancel
            </Button>
          ) : null}
        </ActionBar>
      </div>

      <SimulationProgress
        progress={detail.progress}
        spinCount={detail.spinCount}
        errorMessage={detail.errorMessage}
      />
    </div>
  )
}
