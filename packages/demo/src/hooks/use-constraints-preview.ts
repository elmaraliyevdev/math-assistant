import { useMemo } from 'react'

import { useDemoAnimation } from './use-demo-animation'

const CONSTRAINT_PHASES = [
  { id: 'valid' as const, durationMs: 1800 },
  { id: 'violation' as const, durationMs: 2200 },
  { id: 'resolved' as const, durationMs: 2600 },
]

export type ConstraintsPreviewPhase = (typeof CONSTRAINT_PHASES)[number]['id']

export type ConstraintRuleState = 'pass' | 'error' | 'checking'

export type ConstraintRulePreview = {
  id: string
  label: string
  detail: string
  state: ConstraintRuleState
}

/** Constraint validation loop — distinct from hero symbol drag. */
export function useConstraintsPreview() {
  const { phase } = useDemoAnimation({
    phases: CONSTRAINT_PHASES,
    loop: true,
  })

  const rules: ConstraintRulePreview[] = useMemo(() => {
    const scatterState: ConstraintRuleState =
      phase === 'violation' ? 'error' : phase === 'valid' ? 'pass' : 'pass'

    return [
      {
        id: 'wild-consecutive',
        label: 'Wild max 2 consecutive',
        detail: 'All reels',
        state: 'pass',
      },
      {
        id: 'scatter-distance',
        label: 'Scatter min distance 3',
        detail: 'Strip-wide',
        state: 'pass',
      },
      {
        id: 'scatter-per-reel',
        label: 'Scatter max 2 per reel',
        detail: phase === 'violation' ? 'Reel 3 · 3 found' : 'All reels',
        state: scatterState,
      },
      {
        id: 'bonus-cap',
        label: 'Hold & Win max 1 per strip',
        detail: 'Per reel strip',
        state: 'pass',
      },
    ]
  }, [phase])

  const caption = useMemo(() => {
    switch (phase) {
      case 'valid':
        return 'All constraint rules pass'
      case 'violation':
        return 'Violation flagged on Reel 3'
      case 'resolved':
        return 'Adjust strip — rules revalidate instantly'
    }
  }, [phase])

  const summary = useMemo(() => {
    const errors = rules.filter((r) => r.state === 'error').length
    const passes = rules.filter((r) => r.state === 'pass').length
    return { errors, passes }
  }, [rules])

  return {
    phase,
    rules,
    caption,
    highlightReel: phase === 'violation' ? 2 : undefined,
    showResolved: phase === 'resolved',
    summary,
  }
}
