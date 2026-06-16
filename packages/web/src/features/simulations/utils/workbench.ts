import type { MathConfigSnapshot } from '@/types/api'

type TriggerRow = MathConfigSnapshot['scatterTriggers'][number]

function readTriggers(
  canonical: Record<string, unknown>,
  key: 'scatterTriggers' | 'bonusTriggers',
): TriggerRow[] {
  const machines = canonical.stateMachines as Record<string, unknown> | undefined
  const main = machines?.main as Record<string, unknown> | undefined
  const states = main?.states as Record<string, Record<string, unknown>> | undefined
  if (!states) return []

  const rows: TriggerRow[] = []
  for (const [stateId, state] of Object.entries(states)) {
    const raw = state[key]
    if (!Array.isArray(raw)) continue
    for (const item of raw) {
      if (!item || typeof item !== 'object') continue
      const trigger = item as Record<string, unknown>
      rows.push({
        state: stateId,
        symbolId: String(trigger.symbolId ?? ''),
        minCount: Number(trigger.minCount ?? 0),
        emitTrigger: String(trigger.emitTrigger ?? ''),
      })
    }
  }
  return rows
}

function readJackpotTiers(canonical: Record<string, unknown>): Record<string, number> {
  const machines = canonical.stateMachines as Record<string, unknown> | undefined
  const haw = machines?.hold_and_win as Record<string, unknown> | undefined
  const states = haw?.states as Record<string, Record<string, unknown>> | undefined
  const respins = states?.HAW_RESPINS
  const raw = respins?.pluginConfig as Record<string, unknown> | undefined
  const tiers = raw?.jackpotTiers
  if (!tiers || typeof tiers !== 'object') return {}
  return Object.fromEntries(
    Object.entries(tiers as Record<string, unknown>).map(([tier, value]) => [
      tier,
      Number(value),
    ]),
  )
}

export function extractMathConfigSnapshot(
  canonical: Record<string, unknown>,
): MathConfigSnapshot {
  const metadata = canonical.metadata as Record<string, unknown> | undefined
  const rtpTargetRaw = metadata?.rtpTarget as Record<string, unknown> | undefined
  const rtpTarget =
    rtpTargetRaw && typeof rtpTargetRaw.percent === 'number'
      ? {
          percent: Number(rtpTargetRaw.percent),
          tolerance:
            typeof rtpTargetRaw.tolerance === 'number'
              ? Number(rtpTargetRaw.tolerance)
              : undefined,
        }
      : null

  const runtimeLimits = canonical.runtimeLimits as Record<string, unknown> | undefined
  const exposure = runtimeLimits?.exposure as Record<string, unknown> | undefined

  const paytable = canonical.paytable as Record<string, unknown> | undefined
  const pays = Array.isArray(paytable?.pays) ? paytable.pays : []
  const paytableSummary = pays
    .filter((item): item is Record<string, unknown> => !!item && typeof item === 'object')
    .map((item) => ({
      symbolId: String(item.symbolId ?? ''),
      count: Number(item.count ?? 0),
      multiplier: Number(item.multiplier ?? 0),
    }))

  return {
    rtpTarget,
    scatterTriggers: readTriggers(canonical, 'scatterTriggers'),
    bonusTriggers: readTriggers(canonical, 'bonusTriggers'),
    jackpotTiers: readJackpotTiers(canonical),
    exposureCap: {
      maxWinMinorUnits:
        typeof exposure?.maxWinMinorUnits === 'number'
          ? Number(exposure.maxWinMinorUnits)
          : null,
      maxWinMultiplier:
        typeof exposure?.maxWinMultiplier === 'number'
          ? Number(exposure.maxWinMultiplier)
          : null,
    },
    paytableSummary,
  }
}

export function formatDurationMs(durationMs: number | null | undefined): string {
  if (durationMs == null) return '—'
  if (durationMs < 1000) return `${durationMs} ms`
  const seconds = durationMs / 1000
  if (seconds < 60) return `${seconds.toFixed(1)} s`
  const minutes = Math.floor(seconds / 60)
  const remainder = Math.round(seconds % 60)
  return `${minutes}m ${remainder}s`
}

export interface ComparisonHighlights {
  bestRtpMatchId: string | null
  lowestVolatilityId: string | null
  highestHitFrequencyId: string | null
}

export function deriveComparisonHighlights(
  data: import('@/types/api').SimulationCompareResponse,
): ComparisonHighlights {
  const entries = data.simulations
  if (entries.length === 0) {
    return {
      bestRtpMatchId: null,
      lowestVolatilityId: null,
      highestHitFrequencyId: null,
    }
  }

  let bestRtpMatchId = entries[0].simulationId
  let bestGap = Number.POSITIVE_INFINITY
  let lowestVolatilityId = entries[0].simulationId
  let lowestVolatility = entries[0].results.summary.volatility
  let highestHitFrequencyId = entries[0].simulationId
  let highestHitFrequency = entries[0].results.summary.hitFrequency

  for (const entry of entries) {
    const validation = entry.results.rtpValidation
    if (validation) {
      const gap = Math.abs(validation.difference)
      if (gap < bestGap) {
        bestGap = gap
        bestRtpMatchId = entry.simulationId
      }
    }
    const volatility = entry.results.summary.volatility
    if (volatility < lowestVolatility) {
      lowestVolatility = volatility
      lowestVolatilityId = entry.simulationId
    }
    const hitFrequency = entry.results.summary.hitFrequency
    if (hitFrequency > highestHitFrequency) {
      highestHitFrequency = hitFrequency
      highestHitFrequencyId = entry.simulationId
    }
  }

  return { bestRtpMatchId, lowestVolatilityId, highestHitFrequencyId }
}
