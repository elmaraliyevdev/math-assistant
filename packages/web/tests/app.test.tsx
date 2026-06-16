import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { AppProviders } from '@/app/providers'
import { useThemeStore } from '@/stores/theme-store'

describe('AppProviders', () => {
  it('initializes theme and renders children', () => {
    render(
      <AppProviders>
        <div>child content</div>
      </AppProviders>,
    )

    expect(screen.getByText('child content')).toBeInTheDocument()
    expect(['light', 'dark']).toContain(useThemeStore.getState().theme)
  })
})

describe('utils formatting', () => {
  it('formats dates and numbers', async () => {
    const { formatDate, formatNumber } = await import('@/lib/utils')
    expect(formatDate(null)).toBe('—')
    expect(formatNumber(1200)).toBe('1,200')
  })
})

describe('theme store initialize', () => {
  it('reads stored preference', () => {
    localStorage.setItem('ma_theme', 'dark')
    useThemeStore.getState().initialize()
    expect(useThemeStore.getState().theme).toBe('dark')
  })
})
