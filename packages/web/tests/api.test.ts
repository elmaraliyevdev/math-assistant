import { describe, expect, it, vi } from 'vitest'

import { api, getErrorMessage } from '@/services/api'
import { authService } from '@/services/auth'
import { useAuthStore } from '@/stores/auth-store'
import { refreshTokenStorage } from '@/lib/refresh-token-storage'

describe('getErrorMessage', () => {
  it('extracts API error messages', () => {
    const error = {
      isAxiosError: true,
      message: 'Request failed',
      response: {
        data: { error: { message: 'Invalid credentials' } },
      },
    }

    expect(getErrorMessage(error)).toBe('Invalid credentials')
  })

  it('falls back to generic message', () => {
    expect(getErrorMessage('boom')).toBe('An unexpected error occurred')
  })
})

describe('authService refresh flow', () => {
  it('applies refreshed tokens', async () => {
    refreshTokenStorage.set('old-refresh')
    vi.spyOn(api, 'post').mockResolvedValue({
      data: {
        accessToken: 'new-access',
        refreshToken: 'new-refresh',
        tokenType: 'bearer',
        expiresIn: 900,
      },
    } as never)

    const tokens = await authService.refresh()
    expect(tokens?.accessToken).toBe('new-access')
    expect(useAuthStore.getState().accessToken).toBe('new-access')
    expect(refreshTokenStorage.get()).toBe('new-refresh')
  })
})
