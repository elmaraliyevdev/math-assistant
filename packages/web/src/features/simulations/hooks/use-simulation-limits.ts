import { useEngineVersion } from '@/features/simulations/hooks/use-engine'
import type { EngineVersion } from '@/types/api'

export interface SimulationLimitState {
  spinCountExceeded: boolean
  activeLimitReached: boolean
  guidance: string | null
  limits: EngineVersion | undefined
}

export function evaluateSimulationLimits(
  spinCount: number,
  limits: EngineVersion | undefined,
): SimulationLimitState {
  if (!limits) {
    return {
      spinCountExceeded: false,
      activeLimitReached: false,
      guidance: null,
      limits,
    }
  }

  const spinCountExceeded = spinCount > limits.maxSimulationSpinCount
  const activeLimitReached =
    limits.maxActiveSimulations !== null &&
    limits.activeSimulationCount >= limits.maxActiveSimulations

  let guidance: string | null = null
  if (spinCountExceeded) {
    guidance = `Spin count exceeds the ${limits.deploymentMode} deployment limit of ${limits.maxSimulationSpinCount.toLocaleString()}. Reduce spins or contact your administrator for enterprise limits.`
  } else if (activeLimitReached) {
    guidance = `This deployment allows ${limits.maxActiveSimulations} concurrent simulations (${limits.activeSimulationCount} running). Wait for a simulation to finish or cancel one before starting another.`
  }

  return {
    spinCountExceeded,
    activeLimitReached,
    guidance,
    limits,
  }
}

export function useSimulationLimits(spinCount: number) {
  const engine = useEngineVersion()
  const state = evaluateSimulationLimits(spinCount, engine.data)
  return {
    ...state,
    isLoading: engine.isLoading,
  }
}
