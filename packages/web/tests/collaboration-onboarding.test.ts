import { describe, expect, it } from 'vitest'

import {
  canApproveReview,
  canManageMembers,
  canRecordApproval,
  canReleaseSimulation,
  canRequestReview,
  roleAtLeast,
} from '@/lib/permissions'
import { evaluateSimulationLimits } from '@/features/simulations/hooks/use-simulation-limits'

describe('permissions', () => {
  it('ranks organization roles', () => {
    expect(roleAtLeast('admin', 'developer')).toBe(true)
    expect(roleAtLeast('viewer', 'developer')).toBe(false)
    expect(canManageMembers('admin')).toBe(true)
    expect(canManageMembers('developer')).toBe(false)
    expect(canRequestReview('developer')).toBe(true)
    expect(canApproveReview('developer')).toBe(false)
    expect(canReleaseSimulation('owner')).toBe(true)
    expect(canRecordApproval('admin', 'producer')).toBe(false)
    expect(canRecordApproval('owner', 'producer')).toBe(true)
  })
})

describe('simulation limits', () => {
  it('flags spin and active simulation limits', () => {
    const within = evaluateSimulationLimits(1000, {
      engineVersion: 'runtime-core@1.8.0',
      validatorVersion: 'validation-engine@1.0.0',
      supportedPlugins: [],
      rng: { algorithm: 'PCG64', policy: 'v1-hash-shard' },
      maxRecommendedSpinCount: 10_000_000,
      deploymentMode: 'mvp',
      maxSimulationSpinCount: 10_000_000,
      maxActiveSimulations: 2,
      activeSimulationCount: 1,
    })
    expect(within.guidance).toBeNull()

    const overSpins = evaluateSimulationLimits(20_000_000, within.limits)
    expect(overSpins.spinCountExceeded).toBe(true)
    expect(overSpins.guidance).toMatch(/deployment limit/)

    const atCapacity = evaluateSimulationLimits(1000, {
      ...within.limits!,
      activeSimulationCount: 2,
    })
    expect(atCapacity.activeLimitReached).toBe(true)
    expect(atCapacity.guidance).toMatch(/concurrent simulations/)
  })
})
