import { useEffect, useState } from 'react'
import { toast } from 'sonner'

import { useAuthStore } from '@/stores/auth-store'

const WARNING_BEFORE_MS = 2 * 60 * 1000

export function SessionExpiryNotice({ expiresInSeconds }: { expiresInSeconds: number }) {
  const [warned, setWarned] = useState(false)

  useEffect(() => {
    const warningAt = Math.max(0, expiresInSeconds * 1000 - WARNING_BEFORE_MS)
    const timer = window.setTimeout(() => {
      if (!warned) {
        setWarned(true)
        toast.warning('Your session will expire soon. Save your work and sign in again if needed.')
      }
    }, warningAt)
    return () => window.clearTimeout(timer)
  }, [expiresInSeconds, warned])

  return null
}

export function useSessionExpiryFromToken() {
  const token = useAuthStore((s) => s.accessToken)
  const [expiresIn, setExpiresIn] = useState<number | null>(null)

  useEffect(() => {
    if (!token) {
      setExpiresIn(null)
      return
    }
    try {
      const payload = JSON.parse(atob(token.split('.')[1] ?? '')) as { exp?: number }
      if (payload.exp) {
        const remaining = payload.exp - Math.floor(Date.now() / 1000)
        setExpiresIn(Math.max(0, remaining))
      }
    } catch {
      setExpiresIn(null)
    }
  }, [token])

  return expiresIn
}
