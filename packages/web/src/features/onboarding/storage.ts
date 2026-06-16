const STORAGE_KEY = 'math-assistant-onboarding-completed'

export function isOnboardingCompleted(): boolean {
  if (typeof window === 'undefined') {
    return true
  }
  return window.localStorage.getItem(STORAGE_KEY) === 'true'
}

export function setOnboardingCompleted(): void {
  window.localStorage.setItem(STORAGE_KEY, 'true')
}

export function clearOnboardingCompleted(): void {
  window.localStorage.removeItem(STORAGE_KEY)
}

export type OnboardingStep =
  | 'welcome'
  | 'organization'
  | 'game'
  | 'version'
  | 'simulation'
  | 'results'

export const ONBOARDING_SPIN_COUNT = 100_000

export const ONBOARDING_SAMPLE_JSON = JSON.stringify(
  { schemaVersion: '1.0.0' },
  null,
  2,
)
