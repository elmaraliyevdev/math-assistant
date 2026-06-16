import { describe, expect, it, beforeEach } from 'vitest'

import { useThemeStore } from '@/stores/theme-store'

describe('theme store', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.classList.remove('dark')
  })

  it('toggles dark mode class', () => {
    useThemeStore.getState().setTheme('light')
    expect(document.documentElement.classList.contains('dark')).toBe(false)

    useThemeStore.getState().toggle()
    expect(document.documentElement.classList.contains('dark')).toBe(true)
    expect(useThemeStore.getState().theme).toBe('dark')
  })
})
