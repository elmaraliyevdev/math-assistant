import { http, HttpResponse } from 'msw'
import { beforeEach, describe, expect, it } from 'vitest'

import { api } from '@/services/api'
import { refreshTokenStorage } from '@/lib/refresh-token-storage'
import { useAuthStore } from '@/stores/auth-store'

import { server } from './msw'
import './msw'

describe('401 refresh retry', () => {
  beforeEach(() => {
    useAuthStore.getState().setAccessToken('expired-token')
    refreshTokenStorage.set('refresh-token')
  })

  it('refreshes session and retries the original request', async () => {
    let gameRequests = 0

    server.use(
      http.get('/api/games', () => {
        gameRequests += 1
        if (gameRequests === 1) {
          return HttpResponse.json(
            { error: { code: 'UNAUTHORIZED', message: 'Expired' } },
            { status: 401 },
          )
        }
        return HttpResponse.json({
          items: [],
          total: 0,
          page: 1,
          pageSize: 20,
        })
      }),
    )

    const response = await api.get('/games')
    expect(response.status).toBe(200)
    expect(gameRequests).toBe(2)
    expect(useAuthStore.getState().accessToken).toBe('access-token')
  })
})
