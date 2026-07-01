import { ANALYTICS } from '@/lib/site-config'

type AnalyticsEvent =
  | 'signup'
  | 'demo_opened'
  | 'simulation_started'
  | 'contact_submitted'
  | 'cta_click'

interface EventProperties {
  [key: string]: string | number | boolean | undefined
}

declare global {
  interface Window {
    dataLayer?: unknown[]
    gtag?: (...args: unknown[]) => void
    posthog?: {
      capture: (event: string, properties?: EventProperties) => void
      identify: (id: string, properties?: EventProperties) => void
      reset: () => void
    }
  }
}

let initialized = false

export function initAnalytics() {
  if (initialized || typeof window === 'undefined') {
    return
  }
  initialized = true

  if (ANALYTICS.gaId) {
    const script = document.createElement('script')
    script.async = true
    script.src = `https://www.googletagmanager.com/gtag/js?id=${ANALYTICS.gaId}`
    document.head.appendChild(script)
    window.gtag = function gtag(...args: unknown[]) {
      window.dataLayer = window.dataLayer ?? []
      window.dataLayer.push(args)
    }
    window.gtag('js', new Date())
    window.gtag('config', ANALYTICS.gaId, { send_page_view: false })
  }

  if (ANALYTICS.posthogKey) {
    const script = document.createElement('script')
    script.async = true
    script.src = `${ANALYTICS.posthogHost}/static/array.js`
    script.onload = () => {
      window.posthog?.capture('$pageview')
    }
    document.head.appendChild(script)
  }
}

export function trackPageView(path: string, title?: string) {
  if (ANALYTICS.gaId && window.gtag) {
    window.gtag('event', 'page_view', {
      page_path: path,
      page_title: title,
    })
  }
  window.posthog?.capture('$pageview', { path, title })
}

export function trackEvent(event: AnalyticsEvent, properties?: EventProperties) {
  if (ANALYTICS.gaId && window.gtag) {
    window.gtag('event', event, properties)
  }
  window.posthog?.capture(event, properties)
}

export function identifyUser(userId: string, traits?: EventProperties) {
  window.posthog?.identify(userId, traits)
}

export function resetAnalytics() {
  window.posthog?.reset()
}
