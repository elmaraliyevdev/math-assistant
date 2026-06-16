import type { OnboardingStep } from '@/features/onboarding/storage'

export const ONBOARDING_STEPS: OnboardingStep[] = [
  'welcome',
  'organization',
  'game',
  'version',
  'simulation',
  'results',
]

const STEP_MINUTES: Record<OnboardingStep, number> = {
  welcome: 1,
  organization: 2,
  game: 2,
  version: 3,
  simulation: 2,
  results: 2,
}

export function getOnboardingProgress(step: OnboardingStep): {
  current: number
  total: number
  percent: number
} {
  const current = ONBOARDING_STEPS.indexOf(step) + 1
  const total = ONBOARDING_STEPS.length
  return {
    current,
    total,
    percent: Math.round((current / total) * 100),
  }
}

export function getEstimatedRemainingMinutes(step: OnboardingStep): number {
  const index = ONBOARDING_STEPS.indexOf(step)
  return ONBOARDING_STEPS.slice(index).reduce(
    (sum, item) => sum + STEP_MINUTES[item],
    0,
  )
}
