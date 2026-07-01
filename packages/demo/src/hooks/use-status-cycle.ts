import { useEffect, useState } from 'react'

export type UseStatusCycleOptions<T> = {
  statuses: readonly T[]
  intervalMs?: number
  autoStart?: boolean
  /** Start at this index instead of 0 */
  initialIndex?: number
}

/**
 * Cycles through a list of status labels — validation badges, worker states, etc.
 */
export function useStatusCycle<T>({
  statuses,
  intervalMs = 2000,
  autoStart = true,
  initialIndex = 0,
}: UseStatusCycleOptions<T>) {
  const [index, setIndex] = useState(initialIndex)
  const [isRunning, setIsRunning] = useState(autoStart)

  useEffect(() => {
    if (!isRunning || statuses.length <= 1) return

    const interval = window.setInterval(() => {
      setIndex((current) => (current + 1) % statuses.length)
    }, intervalMs)

    return () => window.clearInterval(interval)
  }, [intervalMs, isRunning, statuses.length])

  const restart = () => {
    setIndex(initialIndex)
    setIsRunning(true)
  }

  return {
    status: statuses[index] ?? statuses[0],
    index,
    isRunning,
    restart,
    pause: () => setIsRunning(false),
    resume: () => setIsRunning(true),
  }
}
