import { describe, expect, it } from 'vitest'

import { formatPercent, cn } from '@/lib/utils'
import { statusBadgeVariant } from '@/components/ui/badge'

describe('utils', () => {
  it('merges class names', () => {
    expect(cn('px-2', false && 'hidden', 'py-1')).toContain('px-2')
  })

  it('formats percentages', () => {
    expect(formatPercent(0.9654)).toBe('96.54%')
  })
})

describe('statusBadgeVariant', () => {
  it('maps statuses to variants', () => {
    expect(statusBadgeVariant('completed')).toBe('success')
    expect(statusBadgeVariant('failed')).toBe('danger')
    expect(statusBadgeVariant('running')).toBe('warning')
  })
})
