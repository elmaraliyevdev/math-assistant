import * as Sentry from '@sentry/react'

const dsn = import.meta.env.VITE_SENTRY_DSN as string | undefined

export function initSentry() {
  if (!dsn) return

  Sentry.init({
    dsn,
    environment: import.meta.env.VITE_SENTRY_ENVIRONMENT ?? 'development',
    integrations: [Sentry.browserTracingIntegration()],
    tracesSampleRate: 0.1,
  })
}

export function captureApiError(error: unknown, context?: Record<string, string>) {
  if (!dsn) return
  Sentry.captureException(error, { extra: context })
}

export { Sentry }
