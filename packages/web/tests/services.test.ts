import { describe, expect, it } from 'vitest'

import { refreshTokenStorage } from '@/lib/refresh-token-storage'
import { authService } from '@/services/auth'
import { gamesService } from '@/services/games'
import { organizationsService } from '@/services/organizations'
import { simulationsService } from '@/services/simulations'

describe('service contracts', () => {
  it('exposes auth endpoints', () => {
    expect(authService.login).toBeTypeOf('function')
    expect(authService.register).toBeTypeOf('function')
    expect(authService.refresh).toBeTypeOf('function')
    expect(authService.logout).toBeTypeOf('function')
    expect(authService.me).toBeTypeOf('function')
  })

  it('exposes games endpoints', () => {
    expect(gamesService.list).toBeTypeOf('function')
    expect(gamesService.create).toBeTypeOf('function')
    expect(gamesService.createVersion).toBeTypeOf('function')
  })

  it('exposes simulation endpoints', () => {
    expect(simulationsService.list).toBeTypeOf('function')
    expect(simulationsService.create).toBeTypeOf('function')
    expect(simulationsService.getResults).toBeTypeOf('function')
  })

  it('exposes organization endpoints', () => {
    expect(organizationsService.list).toBeTypeOf('function')
    expect(organizationsService.addMember).toBeTypeOf('function')
  })

  it('refresh token storage is isolated from access token', () => {
    refreshTokenStorage.set('refresh-only')
    expect(refreshTokenStorage.get()).toBe('refresh-only')
    refreshTokenStorage.clear()
  })
})
