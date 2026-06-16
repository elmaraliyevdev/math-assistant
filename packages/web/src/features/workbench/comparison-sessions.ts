import type { SimulationCompareResponse } from '@/types/api'

const STORAGE_KEY = 'math-assistant-comparison-sessions'

export interface ComparisonSession {
  id: string
  name: string
  simulationIds: string[]
  savedAt: string
  snapshot?: SimulationCompareResponse
}

export function listComparisonSessions(): ComparisonSession[] {
  if (typeof window === 'undefined') {
    return []
  }
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) {
      return []
    }
    return JSON.parse(raw) as ComparisonSession[]
  } catch {
    return []
  }
}

export function saveComparisonSession(
  session: Omit<ComparisonSession, 'id' | 'savedAt'> & { id?: string },
): ComparisonSession {
  const existing = listComparisonSessions()
  const saved: ComparisonSession = {
    id: session.id ?? crypto.randomUUID(),
    name: session.name,
    simulationIds: session.simulationIds,
    savedAt: new Date().toISOString(),
    snapshot: session.snapshot,
  }
  const next = [saved, ...existing.filter((item) => item.id !== saved.id)].slice(0, 20)
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
  return saved
}

export function deleteComparisonSession(sessionId: string): void {
  const next = listComparisonSessions().filter((item) => item.id !== sessionId)
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
}
