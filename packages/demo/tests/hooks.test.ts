import { renderHook, act } from '@testing-library/react'
import { describe, expect, it, vi, afterEach } from 'vitest'

import { useDemoAnimation } from '../src/hooks/use-demo-animation'
import { useDemoClock } from '../src/hooks/use-demo-clock'
import { useDemoSimulation } from '../src/hooks/use-demo-simulation'
import { useDemoTicker } from '../src/hooks/use-demo-ticker'
import { useGaugeAnimation } from '../src/hooks/use-gauge-animation'
import { useHeroWalkthrough } from '../src/hooks/use-hero-walkthrough'
import { useMetricCounter } from '../src/hooks/use-metric-counter'
import { useStatusCycle } from '../src/hooks/use-status-cycle'

afterEach(() => {
  vi.useRealTimers()
})

describe('useDemoTicker', () => {
  it('ticks toward the target value', () => {
    vi.useFakeTimers()
    const { result } = renderHook(() =>
      useDemoTicker({ from: 0, to: 10, intervalMs: 100, step: 2 }),
    )

    expect(result.current.value).toBe(0)
    act(() => {
      vi.advanceTimersByTime(300)
    })
    expect(result.current.value).toBeGreaterThan(0)
  })
})

describe('useDemoAnimation', () => {
  it('advances through phases', () => {
    vi.useFakeTimers()
    const { result } = renderHook(() =>
      useDemoAnimation({
        phases: [
          { id: 'idle', durationMs: 100 },
          { id: 'active', durationMs: 100 },
        ],
      }),
    )

    expect(result.current.phase).toBe('idle')
    act(() => {
      vi.advanceTimersByTime(150)
    })
    expect(result.current.phase).toBe('active')
  })
})

describe('useDemoClock', () => {
  it('formats a relative label from a reference time', () => {
    const reference = new Date(Date.now() - 5 * 60_000).toISOString()
    const { result } = renderHook(() => useDemoClock({ referenceTime: reference }))
    expect(result.current.label).toMatch(/m ago|Just now/)
  })
})

describe('useMetricCounter', () => {
  it('formats the display string', () => {
    vi.useFakeTimers()
    const { result } = renderHook(() =>
      useMetricCounter({
        from: 0,
        to: 1000,
        intervalMs: 100,
        step: 500,
        formatter: (v) => `${v} spins`,
      }),
    )

    expect(result.current.display).toBe('0 spins')
    act(() => {
      vi.advanceTimersByTime(200)
    })
    expect(result.current.display).toMatch(/spins$/)
  })
})

describe('useStatusCycle', () => {
  it('cycles through statuses', () => {
    vi.useFakeTimers()
    const { result } = renderHook(() =>
      useStatusCycle({
        statuses: ['idle', 'running', 'done'] as const,
        intervalMs: 1000,
      }),
    )

    expect(result.current.status).toBe('idle')
    act(() => {
      vi.advanceTimersByTime(1100)
    })
    expect(result.current.status).toBe('running')
  })
})

describe('useGaugeAnimation', () => {
  it('clamps percent between 0 and 100', () => {
    vi.useFakeTimers()
    const { result } = renderHook(() =>
      useGaugeAnimation({ from: 0, to: 50, intervalMs: 50, step: 10 }),
    )

    expect(result.current.percent).toBeGreaterThanOrEqual(0)
    expect(result.current.percent).toBeLessThanOrEqual(100)
  })
})

describe('useDemoSimulation', () => {
  it('exposes spin progress state', () => {
    vi.useFakeTimers()
    const { result } = renderHook(() => useDemoSimulation())

    expect(result.current.status).toBe('running')
    expect(result.current.spinCount).toBeGreaterThan(0)
    expect(result.current.workerProgress).toHaveLength(4)
  })
})

describe('useHeroWalkthrough', () => {
  it('returns phase-driven UI state', () => {
    vi.useFakeTimers()
    const { result } = renderHook(() => useHeroWalkthrough())

    expect(result.current.phase).toBe('idle')
    act(() => {
      vi.advanceTimersByTime(1300)
    })
    expect(result.current.phase).toBe('drag')
    expect(result.current.draggingSymbol).toBe('HV1')
    expect(result.current.showDragPath).toBe(true)
  })
})
