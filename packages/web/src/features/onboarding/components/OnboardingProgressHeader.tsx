import { Progress } from '@/components/ui/progress'
import {
  getEstimatedRemainingMinutes,
  getOnboardingProgress,
  ONBOARDING_STEPS,
} from '@/features/onboarding/progress'
import type { OnboardingStep } from '@/features/onboarding/storage'

function stepLabel(step: OnboardingStep): string {
  switch (step) {
    case 'welcome':
      return 'Welcome'
    case 'organization':
      return 'Organization'
    case 'game':
      return 'Game'
    case 'version':
      return 'Version'
    case 'simulation':
      return 'Simulation'
    case 'results':
      return 'Results'
  }
}

export function OnboardingProgressHeader({ step }: { step: OnboardingStep }) {
  const { current, total, percent } = getOnboardingProgress(step)
  const remainingMinutes = getEstimatedRemainingMinutes(step)

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2 text-sm">
        <span className="font-medium">
          Step {current} of {total}
        </span>
        <span className="text-muted-foreground">
          ~{remainingMinutes} min remaining
        </span>
      </div>
      <Progress value={percent} aria-label="Onboarding progress" />
      <div className="flex flex-wrap gap-2">
        {ONBOARDING_STEPS.map((item, index) => (
          <span
            key={item}
            className={`rounded-full px-3 py-1 text-xs font-medium ${
              index === current - 1
                ? 'bg-primary text-primary-foreground'
                : index < current - 1
                  ? 'bg-muted text-foreground'
                  : 'bg-muted/50 text-muted-foreground'
            }`}
          >
            {index + 1}. {stepLabel(item)}
          </span>
        ))}
      </div>
    </div>
  )
}
