import { useMemo } from 'react'

import { useDemoTicker, type UseDemoTickerOptions } from './use-demo-ticker'

export type UseMetricCounterOptions = UseDemoTickerOptions & {
  /** Format the animated value for display */
  formatter?: (value: number) => string
}

const defaultFormatter = (value: number, precision: number) =>
  value.toLocaleString(undefined, {
    minimumFractionDigits: precision,
    maximumFractionDigits: precision,
  })

/**
 * Animated numeric counter with a display-ready string — spin counts, RTP readouts, etc.
 */
export function useMetricCounter({
  formatter,
  precision = 0,
  ...tickerOptions
}: UseMetricCounterOptions) {
  const ticker = useDemoTicker({ precision, ...tickerOptions })

  const display = useMemo(() => {
    if (formatter) return formatter(ticker.value)
    return defaultFormatter(ticker.value, precision)
  }, [formatter, precision, ticker.value])

  return { ...ticker, display }
}
