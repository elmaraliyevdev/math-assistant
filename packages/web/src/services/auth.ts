import { api } from '@/services/api'
import { refreshTokenStorage } from '@/lib/refresh-token-storage'
import { useAuthStore } from '@/stores/auth-store'
import type {
  MeResponse,
  RegisterResponse,
  TokenResponse,
} from '@/types/api'

export interface LoginInput {
  email: string
  password: string
}

export interface RegisterInput {
  email: string
  password: string
  fullName: string
}

function applyTokens(tokens: TokenResponse) {
  useAuthStore.getState().setAccessToken(tokens.accessToken)
  refreshTokenStorage.set(tokens.refreshToken)
}

export const authService = {
  async register(input: RegisterInput): Promise<RegisterResponse> {
    const { data } = await api.post<RegisterResponse>('/auth/register', input)
    applyTokens(data.tokens)
    return data
  },

  async login(input: LoginInput): Promise<TokenResponse> {
    const { data } = await api.post<TokenResponse>('/auth/login', input)
    applyTokens(data)
    return data
  },

  async refresh(): Promise<TokenResponse | null> {
    const refreshToken = refreshTokenStorage.get()
    if (!refreshToken) {
      return null
    }
    const { data } = await api.post<TokenResponse>('/auth/refresh', {
      refreshToken,
    })
    applyTokens(data)
    return data
  },

  async logout(): Promise<void> {
    const refreshToken = refreshTokenStorage.get()
    if (refreshToken) {
      try {
        await api.post('/auth/logout', { refreshToken })
      } catch {
        // Ignore logout failures when token already expired.
      }
    }
    useAuthStore.getState().clear()
    refreshTokenStorage.clear()
  },

  async me(): Promise<MeResponse> {
    const { data } = await api.get<MeResponse>('/auth/me')
    return data
  },
}
