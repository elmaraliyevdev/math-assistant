export const SPIN_COUNT_PRESETS = [
  { label: '10K', value: 10_000 },
  { label: '100K', value: 100_000 },
  { label: '1M', value: 1_000_000 },
  { label: '10M', value: 10_000_000 },
] as const

export function formatEstimatedRuntime(seconds: number): string {
  if (seconds < 60) {
    return `~${Math.max(1, Math.round(seconds))}s`
  }
  const minutes = Math.floor(seconds / 60)
  const remainder = Math.round(seconds % 60)
  if (minutes < 60) {
    return remainder > 0 ? `~${minutes}m ${remainder}s` : `~${minutes}m`
  }
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return mins > 0 ? `~${hours}h ${mins}m` : `~${hours}h`
}

export function estimateRuntimeSeconds(
  spinCount: number,
  spinsPerSecond: number,
): number {
  if (spinCount <= 0 || spinsPerSecond <= 0) {
    return 0
  }
  return spinCount / spinsPerSecond
}
