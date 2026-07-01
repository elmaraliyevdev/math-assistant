import { useEffect, useState } from 'react'

const RELATIVE_LABELS = [
  { maxSeconds: 60, label: 'Just now' },
  { maxSeconds: 3600, label: 'minutes ago' },
  { maxSeconds: 86400, label: 'hours ago' },
  { maxSeconds: Number.POSITIVE_INFINITY, label: 'days ago' },
] as const

function formatRelative(secondsAgo: number): string {
  if (secondsAgo < 60) return 'Just now'
  if (secondsAgo < 3600) {
    const minutes = Math.floor(secondsAgo / 60)
    return `${minutes}m ago`
  }
  if (secondsAgo < 86400) {
    const hours = Math.floor(secondsAgo / 3600)
    return `${hours}h ago`
  }
  const days = Math.floor(secondsAgo / 86400)
  return `${days}d ago`
}

export type UseDemoClockOptions = {
  /** ISO timestamp treated as the reference "edited at" moment */
  referenceTime?: string
  /** Advance simulated elapsed time every tick */
  tickMs?: number
  /** How many seconds to add per tick */
  secondsPerTick?: number
}

/**
 * Produces a slowly advancing relative time label for demo activity feeds.
 */
export function useDemoClock({
  referenceTime,
  tickMs = 30_000,
  secondsPerTick = 60,
}: UseDemoClockOptions = {}) {
  const [elapsedSeconds, setElapsedSeconds] = useState(0)

  useEffect(() => {
    if (!referenceTime) return
    const referenceMs = new Date(referenceTime).getTime()
    const initial = Math.max(0, Math.floor((Date.now() - referenceMs) / 1000))
    setElapsedSeconds(initial)
  }, [referenceTime])

  useEffect(() => {
    if (!referenceTime) return
    const interval = window.setInterval(() => {
      setElapsedSeconds((current) => current + secondsPerTick)
    }, tickMs)
    return () => window.clearInterval(interval)
  }, [referenceTime, secondsPerTick, tickMs])

  return {
    elapsedSeconds,
    label: formatRelative(elapsedSeconds),
    bucket: RELATIVE_LABELS.find((entry) => elapsedSeconds < entry.maxSeconds)?.label,
  }
}
