import type { SimulationResults } from '@/types/api'

export type HealthVerdict = {
  score: number
  label: string
  tone: 'success' | 'warning' | 'destructive'
}

export function computeSimulationHealth(results: SimulationResults): HealthVerdict {
  if (results.simulationIntelligence?.designVsReality.length) {
    const items = results.simulationIntelligence.designVsReality
    const avg =
      items.reduce((sum, item) => sum + item.confidence.score, 0) / items.length
    const redCount = items.filter((item) => item.status === 'red').length
    const score = Math.round(Math.max(0, avg - redCount * 8))
    return verdictFromScore(score)
  }

  let score = 78
  if (results.rtpValidation) {
    const diff = Math.abs(results.rtpValidation.difference)
    score = results.rtpValidation.withinTolerance
      ? 95
      : diff < 0.005
        ? 88
        : diff < 0.01
          ? 78
          : diff < 0.02
            ? 62
            : 42
  }

  const critical = results.recommendations.filter((r) => r.severity === 'critical').length
  const warnings = results.recommendations.filter((r) => r.severity === 'warning').length
  score -= critical * 12 + warnings * 4
  score = Math.max(0, Math.min(100, Math.round(score)))

  return verdictFromScore(score)
}

function verdictFromScore(score: number): HealthVerdict {
  if (score >= 90) {
    return { score, label: 'Production ready', tone: 'success' }
  }
  if (score >= 70) {
    return { score, label: 'Needs attention', tone: 'warning' }
  }
  return { score, label: 'Critical issues', tone: 'destructive' }
}

export function simulationDurationMs(
  createdAt: string,
  completedAt: string | null,
): number | null {
  if (!completedAt) return null
  const start = new Date(createdAt).getTime()
  const end = new Date(completedAt).getTime()
  if (Number.isNaN(start) || Number.isNaN(end) || end < start) return null
  return end - start
}
