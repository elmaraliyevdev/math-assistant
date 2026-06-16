import { RouterProvider } from '@tanstack/react-router'
import { StrictMode, useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'

import { AppProviders } from '@/app/providers'
import { router } from '@/app/router'
import { initSentry } from '@/lib/sentry'
import { authService } from '@/services/auth'
import { refreshTokenStorage } from '@/lib/refresh-token-storage'
import { useAuthStore } from '@/stores/auth-store'
import '@/index.css'

initSentry()

function Bootstrap({ children }: { children: React.ReactNode }) {
  const [ready, setReady] = useState(false)

  useEffect(() => {
    let cancelled = false

    async function restoreSession() {
      if (useAuthStore.getState().isAuthenticated()) {
        return
      }
      if (!refreshTokenStorage.get()) {
        return
      }
      try {
        await authService.refresh()
      } catch {
        refreshTokenStorage.clear()
        useAuthStore.getState().clear()
      }
    }

    void restoreSession().finally(() => {
      if (!cancelled) {
        setReady(true)
      }
    })

    return () => {
      cancelled = true
    }
  }, [])

  if (!ready) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-muted-foreground">Loading…</p>
      </div>
    )
  }

  return children
}

function App() {
  return (
    <AppProviders>
      <Bootstrap>
        <RouterProvider router={router} />
      </Bootstrap>
    </AppProviders>
  )
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
