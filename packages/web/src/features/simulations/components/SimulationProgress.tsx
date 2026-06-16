import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import type { SimulationProgress as SimulationProgressType } from '@/types/api'
import { formatNumber } from '@/lib/utils'

interface SimulationProgressProps {
  progress: SimulationProgressType
  spinCount: number
  loading?: boolean
  errorMessage?: string | null
}

export function SimulationProgress({
  progress,
  spinCount,
  loading,
  errorMessage,
}: SimulationProgressProps) {
  if (loading) {
    return <Skeleton className="h-28 w-full" />
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Progress</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="h-3 overflow-hidden rounded-full bg-muted">
          <div
            className="h-full bg-primary transition-all duration-500"
            style={{ width: `${Math.min(progress.percentage, 100)}%` }}
            role="progressbar"
            aria-valuenow={progress.percentage}
            aria-valuemin={0}
            aria-valuemax={100}
          />
        </div>
        <div className="flex flex-wrap items-center justify-between gap-2 text-sm text-muted-foreground">
          <span>
            {formatNumber(progress.completedSpins)} / {formatNumber(spinCount)}{' '}
            spins completed
          </span>
          <span className="font-medium text-foreground">
            {progress.percentage.toFixed(1)}%
          </span>
        </div>
        {errorMessage && (
          <p className="text-sm text-destructive">{errorMessage}</p>
        )}
      </CardContent>
    </Card>
  )
}
