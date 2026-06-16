import { describe, expect, it } from 'vitest'

import {
  formatMetricNumber,
  formatMetricPercent,
} from '@/features/simulations/components/MetricsCards'
import { isSimulationActive } from '@/features/simulations/hooks/use-simulations'

describe('simulation helpers', () => {
  it('formats metric values', () => {
    expect(formatMetricPercent(0.5)).toBe('50.00%')
    expect(formatMetricNumber(1000)).toBe('1,000')
  })

  it('treats terminal statuses as inactive', () => {
    expect(isSimulationActive('failed')).toBe(false)
    expect(isSimulationActive('cancelled')).toBe(false)
    expect(isSimulationActive(undefined)).toBe(false)
  })
})
