export const SITE = {
  name: 'MathStudio',
  url: import.meta.env.VITE_SITE_URL ?? 'https://app.mathstudio.app',
} as const

export const ANALYTICS = {
  posthogKey: import.meta.env.VITE_POSTHOG_KEY ?? '',
  posthogHost: import.meta.env.VITE_POSTHOG_HOST ?? 'https://us.i.posthog.com',
  gaId: import.meta.env.VITE_GA_ID ?? '',
} as const
