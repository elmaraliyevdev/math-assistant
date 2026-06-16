const REFRESH_COOKIE_NAME = 'ma_refresh_token'
const REFRESH_STORAGE_KEY = 'ma_refresh_token'

/**
 * Refresh token storage abstraction.
 *
 * True HttpOnly cookies must be set by the API via Set-Cookie. Until the backend
 * supports that, tokens from login/register are mirrored in a SameSite=Strict
 * cookie and sessionStorage so sessions survive reloads without exposing the
 * access token.
 */
export const refreshTokenStorage = {
  get(): string | null {
    if (typeof document === 'undefined') {
      return null
    }

    const cookieMatch = document.cookie
      .split('; ')
      .find((row) => row.startsWith(`${REFRESH_COOKIE_NAME}=`))

    if (cookieMatch) {
      return decodeURIComponent(cookieMatch.split('=')[1] ?? '')
    }

    return sessionStorage.getItem(REFRESH_STORAGE_KEY)
  },

  set(token: string): void {
    sessionStorage.setItem(REFRESH_STORAGE_KEY, token)
    const maxAge = 30 * 24 * 60 * 60
    document.cookie = `${REFRESH_COOKIE_NAME}=${encodeURIComponent(token)}; path=/; SameSite=Strict; max-age=${maxAge}`
  },

  clear(): void {
    sessionStorage.removeItem(REFRESH_STORAGE_KEY)
    document.cookie = `${REFRESH_COOKIE_NAME}=; path=/; max-age=0`
  },
}
