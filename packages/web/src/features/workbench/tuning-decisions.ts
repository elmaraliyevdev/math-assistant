export type TuningDecisionStatus = 'pending' | 'accepted' | 'rejected'

export interface TuningDecision {
  recommendationKey: string
  title: string
  description: string
  status: TuningDecisionStatus
  note: string
  updatedAt: string
}

const storageKey = (simulationId: string) =>
  `math-assistant-tuning-decisions:${simulationId}`

export function listTuningDecisions(simulationId: string): TuningDecision[] {
  if (typeof window === 'undefined') {
    return []
  }
  try {
    const raw = window.localStorage.getItem(storageKey(simulationId))
    return raw ? (JSON.parse(raw) as TuningDecision[]) : []
  } catch {
    return []
  }
}

export function upsertTuningDecision(
  simulationId: string,
  decision: Omit<TuningDecision, 'updatedAt'> & { updatedAt?: string },
): TuningDecision[] {
  const current = listTuningDecisions(simulationId)
  const saved: TuningDecision = {
    ...decision,
    updatedAt: decision.updatedAt ?? new Date().toISOString(),
  }
  const next = [
    saved,
    ...current.filter((item) => item.recommendationKey !== saved.recommendationKey),
  ]
  window.localStorage.setItem(storageKey(simulationId), JSON.stringify(next))
  return next
}

export function buildReviewPacketNote(decisions: TuningDecision[]): string {
  const lines = decisions.map((item) => {
    const note = item.note ? ` — ${item.note}` : ''
    return `- [${item.status.toUpperCase()}] ${item.title}${note}`
  })
  return `Tuning review packet:\n${lines.join('\n')}`
}
