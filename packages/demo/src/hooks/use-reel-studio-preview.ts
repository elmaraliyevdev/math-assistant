import { useMemo } from 'react'

import { useDemoAnimation } from './use-demo-animation'
import { useMetricCounter } from './use-metric-counter'

const STRIP_PREVIEW_PHASES = [
  { id: 'baseline' as const, durationMs: 1600 },
  { id: 'editing' as const, durationMs: 1400 },
  { id: 'updated' as const, durationMs: 2400 },
]

export type ReelStudioPreviewPhase = (typeof STRIP_PREVIEW_PHASES)[number]['id']

const BASE_SCATTER = 11.2
const TARGET_SCATTER = 12.4

/** Distribution-focused loop — distinct from the hero column-grid walkthrough. */
export function useReelStudioPreview() {
  const { phase } = useDemoAnimation({
    phases: STRIP_PREVIEW_PHASES,
    loop: true,
  })

  const scatterCounter = useMetricCounter({
    from: BASE_SCATTER,
    to: TARGET_SCATTER,
    intervalMs: 45,
    step: 0.08,
    precision: 1,
    autoStart: phase === 'updated',
  })

  const scatterPercent = phase === 'baseline' ? BASE_SCATTER : scatterCounter.value

  const caption = useMemo(() => {
    switch (phase) {
      case 'baseline':
        return 'Five reel strips — edit any row directly'
      case 'editing':
        return 'Insert Scatter on reel 3…'
      case 'updated':
        return 'Symbol distribution recalculates instantly'
    }
  }, [phase])

  return {
    phase,
    activeReel: phase !== 'baseline' ? 2 : undefined,
    showInsertion: phase === 'editing' || phase === 'updated',
    scatterPercent,
    wildPercent: 8.1,
    crownPercent: 18.2,
    showPass: phase === 'updated',
    caption,
  }
}
