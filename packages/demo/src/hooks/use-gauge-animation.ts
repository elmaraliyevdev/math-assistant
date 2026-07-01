import { useDemoTicker, type UseDemoTickerOptions } from './use-demo-ticker'

export type UseGaugeAnimationOptions = Omit<UseDemoTickerOptions, 'precision'> & {
  precision?: number
}

/**
 * Smoothly animates a gauge needle or arc toward a target percentage.
 */
export function useGaugeAnimation({
  precision = 2,
  ...options
}: UseGaugeAnimationOptions) {
  const ticker = useDemoTicker({ precision, ...options })

  return {
    value: ticker.value,
    percent: Math.min(100, Math.max(0, ticker.value)),
    isRunning: ticker.isRunning,
    restart: ticker.restart,
    pause: ticker.pause,
  }
}
