import { beforeEach, describe, expect, it } from 'vitest'

import { isOnboardingCompleted, setOnboardingCompleted, clearOnboardingCompleted } from '@/features/onboarding/storage'

describe('onboarding storage', () => {
  beforeEach(() => {
    clearOnboardingCompleted()
  })

  it('tracks completion in localStorage', () => {
    expect(isOnboardingCompleted()).toBe(false)
    setOnboardingCompleted()
    expect(isOnboardingCompleted()).toBe(true)
  })
})
