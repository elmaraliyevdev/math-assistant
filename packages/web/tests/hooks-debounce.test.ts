import { act, renderHook } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { useDebouncedValue } from '@/hooks/use-debounced-value'

describe('useDebouncedValue', () => {
  it('returns the initial value immediately', () => {
    const { result } = renderHook(() => useDebouncedValue('hello', 50))
    expect(result.current).toBe('hello')
  })

  it('updates after the debounce delay', () => {
    vi.useFakeTimers()
    const { result, rerender } = renderHook(
      ({ value }) => useDebouncedValue(value, 100),
      { initialProps: { value: 'a' } },
    )

    rerender({ value: 'b' })
    expect(result.current).toBe('a')

    act(() => {
      vi.advanceTimersByTime(100)
    })
    expect(result.current).toBe('b')
    vi.useRealTimers()
  })
})

describe('toast helpers', () => {
  it('exports toast methods', async () => {
    const { toast } = await import('@/lib/toast')
    expect(typeof toast.success).toBe('function')
    expect(typeof toast.error).toBe('function')
  })
})
