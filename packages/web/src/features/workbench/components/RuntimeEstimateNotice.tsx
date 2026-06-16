import { formatEstimatedRuntime, estimateRuntimeSeconds } from '@/features/workbench/runtime-estimate'

interface RuntimeEstimateNoticeProps {
  spinCount: number
  spinsPerSecond?: number
  source?: string
  sampleCount?: number
}

export function RuntimeEstimateNotice({
  spinCount,
  spinsPerSecond,
  source,
  sampleCount,
}: RuntimeEstimateNoticeProps) {
  if (!spinsPerSecond || spinCount <= 0) {
    return null
  }

  const seconds = estimateRuntimeSeconds(spinCount, spinsPerSecond)
  const sourceLabel =
    source === 'historical'
      ? `based on ${sampleCount ?? 0} completed simulation(s)`
      : 'based on deployment fallback throughput'

  return (
    <p className="text-sm text-muted-foreground">
      Estimated runtime:{' '}
      <span className="font-medium text-foreground">
        {formatEstimatedRuntime(seconds)}
      </span>{' '}
      ({sourceLabel}, {Math.round(spinsPerSecond).toLocaleString()} spins/sec)
    </p>
  )
}
