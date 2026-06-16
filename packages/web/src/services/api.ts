import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'

import { captureApiError } from '@/lib/sentry'
import { refreshTokenStorage } from '@/lib/refresh-token-storage'
import { useAuthStore } from '@/stores/auth-store'

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

let refreshPromise: Promise<string | null> | null = null

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = refreshTokenStorage.get()
  if (!refreshToken) {
    return null
  }

  const response = await axios.post<{
    accessToken: string
    refreshToken: string
  }>(`${API_BASE_URL}/auth/refresh`, { refreshToken })

  const { accessToken, refreshToken: nextRefresh } = response.data
  useAuthStore.getState().setAccessToken(accessToken)
  refreshTokenStorage.set(nextRefresh)
  return accessToken
}

export function setAuthHeader(token: string | null) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`
  } else {
    delete api.defaults.headers.common.Authorization
  }
}

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = useAuthStore.getState().accessToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean
    }

    if (
      error.response?.status !== 401 ||
      !original ||
      original._retry ||
      original.url?.includes('/auth/login') ||
      original.url?.includes('/auth/register') ||
      original.url?.includes('/auth/refresh')
    ) {
      if (error.response && error.response.status >= 500) {
        captureApiError(error, {
          url: original?.url ?? 'unknown',
          method: original?.method ?? 'unknown',
        })
      }
      return Promise.reject(error)
    }

    original._retry = true

    if (!refreshPromise) {
      refreshPromise = refreshAccessToken()
        .catch(() => null)
        .finally(() => {
          refreshPromise = null
        })
    }

    const accessToken = await refreshPromise
    if (!accessToken) {
      useAuthStore.getState().clear()
      refreshTokenStorage.clear()
      setAuthHeader(null)
      return Promise.reject(error)
    }

    original.headers.Authorization = `Bearer ${accessToken}`
    return api(original)
  },
)

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as { error?: { message?: string } } | undefined
    return data?.error?.message ?? error.message
  }
  if (error instanceof Error) {
    return error.message
  }
  return 'An unexpected error occurred'
}
