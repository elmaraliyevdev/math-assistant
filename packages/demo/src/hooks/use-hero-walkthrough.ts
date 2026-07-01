import { useMemo } from 'react'

import { useDemoAnimation } from './use-demo-animation'
import { useMetricCounter } from './use-metric-counter'

export type HeroPhase =
  | 'idle'
  | 'drag'
  | 'drop'
  | 'validate'
  | 'feedback'

const HERO_PHASES = [
  { id: 'idle' as const, durationMs: 1200 },
  { id: 'drag' as const, durationMs: 1800 },
  { id: 'drop' as const, durationMs: 900 },
  { id: 'validate' as const, durationMs: 1100 },
  { id: 'feedback' as const, durationMs: 2800 },
]

export type HeroValidationStatus = 'idle' | 'checking' | 'pass'

const DROP_REEL = 2
const DROP_SLOT = 2

/**
 * Orchestrates the hero reel-studio drag loop — Crown onto Reel 3.
 */
export function useHeroWalkthrough() {
  const { phase } = useDemoAnimation<HeroPhase>({
    phases: HERO_PHASES,
    loop: true,
  })

  const rtpTarget = phase === 'feedback' ? 95.98 : 95.94

  const rtpCounter = useMetricCounter({
    from: 95.94,
    to: rtpTarget,
    intervalMs: 70,
    step: 0.05,
    precision: 2,
    autoStart: phase === 'validate' || phase === 'feedback',
  })

  const validationStatus: HeroValidationStatus = useMemo(() => {
    if (phase === 'validate') return 'checking'
    if (phase === 'feedback' || phase === 'drop') return 'pass'
    return 'idle'
  }, [phase])

  const draggingSymbol = phase === 'drag' ? 'HV1' : null
  const showDragPath = phase === 'drag'
  const showDropZone = phase === 'drag' || phase === 'drop'
  const placedSymbol = phase === 'drop' || phase === 'validate' || phase === 'feedback' ? 'HV1' : null

  const activePaletteSymbol = phase === 'idle' || phase === 'drag' ? 'HV1' : null

  return {
    phase,
    draggingSymbol,
    showDragPath,
    showDropZone,
    placedSymbol,
    dropTargetReel: showDropZone ? DROP_REEL : undefined,
    dropSlotIndex: showDropZone ? DROP_SLOT : undefined,
    activePaletteSymbol,
    rtp: rtpCounter.value,
    validationStatus,
    distribution: {
      wild: 8.1,
      scatter: 2.4,
      holdWin: 1.2,
      hitFrequency: 32.2,
    },
    showConstraintsPass: validationStatus === 'pass',
  }
}
