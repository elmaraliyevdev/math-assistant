import { useCallback, useEffect, useRef, useState } from 'react'

export type DemoAnimationPhase<T extends string> = {
  id: T
  durationMs: number
}

export type UseDemoAnimationOptions<T extends string> = {
  phases: DemoAnimationPhase<T>[]
  loop?: boolean
  autoStart?: boolean
  onPhaseChange?: (phase: T) => void
}

/**
 * Steps through named phases on a timer — useful for hero loops without APIs.
 */
export function useDemoAnimation<T extends string>({
  phases,
  loop = true,
  autoStart = true,
  onPhaseChange,
}: UseDemoAnimationOptions<T>) {
  const [phaseIndex, setPhaseIndex] = useState(0)
  const [isRunning, setIsRunning] = useState(autoStart)
  const onPhaseChangeRef = useRef(onPhaseChange)
  onPhaseChangeRef.current = onPhaseChange

  const phase = phases[phaseIndex]?.id ?? phases[0]?.id
  const durationMs = phases[phaseIndex]?.durationMs ?? 0

  useEffect(() => {
    if (!isRunning || phases.length === 0) return
    if (phase) onPhaseChangeRef.current?.(phase)

    const timeout = window.setTimeout(() => {
      setPhaseIndex((current) => {
        const next = current + 1
        if (next < phases.length) return next
        return loop ? 0 : current
      })
    }, durationMs)

    return () => window.clearTimeout(timeout)
  }, [durationMs, isRunning, loop, phase, phases])

  const restart = useCallback(() => {
    setPhaseIndex(0)
    setIsRunning(true)
  }, [])

  const pause = useCallback(() => setIsRunning(false), [])
  const resume = useCallback(() => setIsRunning(true), [])

  return {
    phase,
    phaseIndex,
    isRunning,
    restart,
    pause,
    resume,
  }
}
