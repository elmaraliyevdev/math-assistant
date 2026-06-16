import { Button } from '@/components/ui/button'
import { SPIN_COUNT_PRESETS } from '@/features/workbench/runtime-estimate'

interface SpinCountPresetsProps {
  value: number
  maxSpinCount?: number
  onSelect: (spinCount: number) => void
}

export function SpinCountPresets({
  value,
  maxSpinCount,
  onSelect,
}: SpinCountPresetsProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {SPIN_COUNT_PRESETS.map((preset) => {
        const disabled = maxSpinCount != null && preset.value > maxSpinCount
        return (
          <Button
            key={preset.label}
            type="button"
            size="sm"
            variant={value === preset.value ? 'default' : 'outline'}
            disabled={disabled}
            onClick={() => onSelect(preset.value)}
          >
            {preset.label}
          </Button>
        )
      })}
    </div>
  )
}
