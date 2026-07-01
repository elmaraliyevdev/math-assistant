import { useEffect, useState } from 'react'

export type UseDemoTickerOptions = {
  /** Starting numeric value */
  from: number
  /** Target value to approach */
  to: number
  /** Milliseconds between ticks */
  intervalMs?: number
  /** Maximum step per tick (absolute) */
  step?: number
  /** Decimal places when rounding */
  precision?: number
  /** Start ticking immediately */
  autoStart?: boolean
  /** Pause when within this distance of `to` */
  settleThreshold?: number
}

/**
 * Smoothly animates a number toward a target — e.g. spin counts or RTP readouts.
 */
export function useDemoTicker({
  from,
  to,
  intervalMs = 80,
  step = 1,
  precision = 2,
  autoStart = true,
  settleThreshold = 0.001,
}: UseDemoTickerOptions) {
  const [value, setValue] = useState(from)
  const [isRunning, setIsRunning] = useState(autoStart)

  useEffect(() => {
    setValue(from)
  }, [from])

  useEffect(() => {
    if (!isRunning) return

    const interval = window.setInterval(() => {
      setValue((current) => {
        const delta = to - current
        if (Math.abs(delta) <= settleThreshold) {
          setIsRunning(false)
          return Number(to.toFixed(precision))
        }
        const direction = delta > 0 ? 1 : -1
        const next = current + direction * Math.min(Math.abs(delta), step)
        return Number(next.toFixed(precision))
      })
    }, intervalMs)

    return () => window.clearInterval(interval)
  }, [intervalMs, isRunning, precision, settleThreshold, step, to])

  const restart = () => {
    setValue(from)
    setIsRunning(true)
  }

  return { value, isRunning, restart, pause: () => setIsRunning(false) }
}
