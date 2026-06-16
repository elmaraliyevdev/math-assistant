import { describe, expect, it } from 'vitest'

import { api, getErrorMessage, setAuthHeader } from '@/services/api'
import { useAuthStore } from '@/stores/auth-store'

import './msw'

describe('api interceptors', () => {
  it('attaches bearer token to requests', async () => {
    useAuthStore.getState().setAccessToken('header-token')
    const response = await api.get('/auth/me')
    expect(response.data.user.email).toBe('user@example.com')
  })

  it('sets and clears default auth header', () => {
    setAuthHeader('abc')
    expect(api.defaults.headers.common.Authorization).toBe('Bearer abc')
    setAuthHeader(null)
    expect(api.defaults.headers.common.Authorization).toBeUndefined()
  })
})

describe('getErrorMessage branches', () => {
  it('returns axios message when no api error body', () => {
    expect(
      getErrorMessage({
        isAxiosError: true,
        message: 'Network down',
      }),
    ).toBe('Network down')
  })
})
