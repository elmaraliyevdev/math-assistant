import { CollapsibleSection } from '@/components/studio/CollapsibleSection'
import { VisualMeter } from '@/components/studio/VisualMeter'
import { useGeneratorStudio } from '@/features/reel-studio/generator/context/generator-context'
import type { FeatureFrequencyGoal, VolatilityGoal } from '@/features/reel-studio/generator/types'
import { cn } from '@/lib/utils'

const VOLATILITY_OPTIONS: Array<{ value: VolatilityGoal; label: string }> = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
]

const FEATURE_OPTIONS: Array<{ value: FeatureFrequencyGoal; label: string }> = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
]

function SegmentedControl<T extends string>({
  value,
  options,
  onChange,
}: {
  value: T
  options: Array<{ value: T; label: string }>
  onChange: (value: T) => void
}) {
  return (
    <div className="flex gap-1 rounded-lg bg-muted/50 p-1">
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          onClick={() => onChange(option.value)}
          className={cn(
            'flex-1 rounded-md px-2 py-2 text-xs font-medium transition-colors duration-150',
            value === option.value
              ? 'bg-background text-foreground shadow-sm'
              : 'text-muted-foreground hover:text-foreground',
          )}
        >
          {option.label}
        </button>
      ))}
    </div>
  )
}

export function DesignGoalsContent() {
  const {
    designGoals,
    seed,
    candidateCount,
    setDesignGoals,
    setSeed,
    setCandidateCount,
  } = useGeneratorStudio()

  return (
    <div className="space-y-4">
      <VisualMeter
        compact
        label="Target RTP"
        value={designGoals.targetRtpPercent}
        min={85}
        max={99}
        unit="%"
        onChange={(targetRtpPercent) => setDesignGoals({ targetRtpPercent })}
      />
      <VisualMeter
        compact
        label="Hit rate"
        value={designGoals.hitRatePercent}
        min={10}
        max={60}
        unit="%"
        onChange={(hitRatePercent) => setDesignGoals({ hitRatePercent })}
      />
      <VisualMeter
        compact
        label="Max win"
        value={designGoals.maximumWinMultiplier}
        min={100}
        max={10000}
        unit="x"
        onChange={(maximumWinMultiplier) => setDesignGoals({ maximumWinMultiplier })}
      />

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <p className="text-xs font-medium text-muted-foreground">Volatility</p>
          <SegmentedControl
            value={designGoals.volatility}
            options={VOLATILITY_OPTIONS}
            onChange={(volatility) => setDesignGoals({ volatility })}
          />
        </div>
        <div className="space-y-2">
          <p className="text-xs font-medium text-muted-foreground">Feature freq.</p>
          <SegmentedControl
            value={designGoals.featureFrequency}
            options={FEATURE_OPTIONS}
            onChange={(featureFrequency) => setDesignGoals({ featureFrequency })}
          />
        </div>
      </div>

      <CollapsibleSection title="Advanced" subtitle="Spacing & generation">
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <VisualMeter
              compact
              label="Wild spacing"
              value={designGoals.wildEveryNSymbols}
              min={8}
              max={80}
              unit=""
              onChange={(wildEveryNSymbols) => setDesignGoals({ wildEveryNSymbols })}
            />
            <VisualMeter
              compact
              label="Scatter spacing"
              value={designGoals.scatterEveryNSymbols}
              min={20}
              max={120}
              unit=""
              onChange={(scatterEveryNSymbols) => setDesignGoals({ scatterEveryNSymbols })}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <VisualMeter
              compact
              label="Reels"
              value={designGoals.reelCount}
              min={3}
              max={6}
              unit=""
              onChange={(reelCount) => setDesignGoals({ reelCount })}
            />
            <VisualMeter
              compact
              label="Length"
              value={designGoals.reelLength}
              min={20}
              max={120}
              unit=""
              onChange={(reelLength) => setDesignGoals({ reelLength })}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <VisualMeter
              compact
              label="Seed"
              value={seed}
              min={1}
              max={9999}
              unit=""
              onChange={setSeed}
            />
            <VisualMeter
              compact
              label="Candidates"
              value={candidateCount}
              min={1}
              max={6}
              unit=""
              onChange={setCandidateCount}
            />
          </div>
        </div>
      </CollapsibleSection>
    </div>
  )
}

/** @deprecated Use DesignGoalsContent inside DesignInspector accordion */
export function DesignGoalsPanel() {
  return <DesignGoalsContent />
}
