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
  rememberMe?: boolean
}

export interface RegisterInput {
  email: string
  password: string
  fullName: string
}

function applyTokens(tokens: TokenResponse, rememberMe = false) {
  useAuthStore.getState().setAccessToken(tokens.accessToken)
  refreshTokenStorage.set(tokens.refreshToken, rememberMe)
}

export const authService = {
  async register(input: RegisterInput): Promise<RegisterResponse> {
    const { data } = await api.post<RegisterResponse>('/auth/register', input)
    applyTokens(data.tokens)
    return data
  },

  async login(input: LoginInput): Promise<TokenResponse> {
    const { data } = await api.post<TokenResponse>('/auth/login', {
      email: input.email,
      password: input.password,
      rememberMe: input.rememberMe ?? false,
    })
    applyTokens(data, input.rememberMe)
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

  async forgotPassword(input: { email: string }): Promise<{ message: string }> {
    const { data } = await api.post<{ message: string }>('/auth/forgot-password', input)
    return data
  },

  async resetPassword(input: { token: string; password: string }): Promise<void> {
    await api.post('/auth/reset-password', input)
  },

  async verifyEmail(input: { token: string }): Promise<void> {
    await api.post('/auth/verify-email', input)
  },

  async resendVerification(): Promise<{ message: string }> {
    const { data } = await api.post<{ message: string }>('/auth/resend-verification')
    return data
  },
}
