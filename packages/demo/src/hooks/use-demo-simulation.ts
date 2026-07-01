import { useMemo } from 'react'

import { useDemoAnimation } from './use-demo-animation'
import { useMetricCounter } from './use-metric-counter'

export type SimulationStatus = 'queued' | 'running' | 'completed'

export type UseDemoSimulationOptions = {
  targetSpins?: number
  initialSpins?: number
  autoStart?: boolean
}

const SIMULATION_PHASES = [
  { id: 'running' as const, durationMs: 12_000 },
  { id: 'completed' as const, durationMs: 3_000 },
]

/**
 * Drives Monte Carlo simulation previews — spin progress, status, and worker fill.
 * Demo UIs consume this state; they never own timers.
 */
export function useDemoSimulation({
  targetSpins = 10_000_000,
  initialSpins = 5_720_000,
  autoStart = true,
}: UseDemoSimulationOptions = {}) {
  const { phase } = useDemoAnimation({
    phases: SIMULATION_PHASES,
    loop: true,
    autoStart,
  })

  const status: SimulationStatus = phase === 'completed' ? 'completed' : 'running'

  const spinTarget =
    status === 'completed' ? targetSpins : Math.round(targetSpins * 0.92)

  const counter = useMetricCounter({
    from: initialSpins,
    to: spinTarget,
    intervalMs: 700,
    step: 85_000,
    precision: 0,
    autoStart: status === 'running',
    formatter: (value) => `${(value / 1_000_000).toFixed(2)}M`,
  })

  const progress = useMemo(
    () => Math.min(100, (counter.value / targetSpins) * 100),
    [counter.value, targetSpins],
  )

  const rtp = useMemo(() => {
    if (status === 'completed') return 95.96
    return 95.7 + (progress / 100) * 0.26
  }, [progress, status])

  const volatility = useMemo(() => {
    if (status === 'completed') return 4.18
    return 4.24 - (progress / 100) * 0.06
  }, [progress, status])

  const rtpDisplay = `${rtp.toFixed(2)}%`
  const volatilityDisplay = volatility.toFixed(2)

  const workerProgress = useMemo(() => {
    const base = [100, 100, 78, 34]
    if (status === 'completed') return base.map(() => 100)
    const boost = counter.value > 5_000_000 ? 15 : 0
    return base.map((value) => (value === 100 ? 100 : Math.min(100, value + boost)))
  }, [counter.value, status])

  return {
    spinCount: counter.value,
    spinDisplay: counter.display,
    progress,
    status,
    rtp,
    rtpDisplay,
    volatility,
    volatilityDisplay,
    workerProgress,
    targetSpins,
  }
}
