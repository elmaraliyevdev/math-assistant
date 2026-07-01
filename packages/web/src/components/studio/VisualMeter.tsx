import { cn } from '@/lib/utils'

export function VisualMeter({
  label,
  value,
  min = 0,
  max = 100,
  unit = '%',
  target,
  current,
  onChange,
  compact = false,
  className,
}: {
  label: string
  value?: number
  min?: number
  max?: number
  unit?: string
  target?: number
  current?: number
  onChange?: (value: number) => void
  className?: string
  compact?: boolean
}) {
  const display = value ?? 0
  const percent = ((display - min) / (max - min)) * 100

  return (
    <div className={cn(compact ? 'space-y-1.5' : 'space-y-2', className)}>
      <div className="flex items-end justify-between gap-2">
        <span className="text-xs font-medium text-muted-foreground">{label}</span>
        <span
          className={cn(
            'font-semibold tabular-nums tracking-tight',
            compact ? 'text-sm' : 'text-lg',
          )}
        >
          {display}
          {unit}
        </span>
      </div>
      {onChange ? (
        <input
          type="range"
          min={min}
          max={max}
          value={display}
          onChange={(event) => onChange(Number(event.target.value))}
          className="studio-range w-full"
        />
      ) : (
        <div className="h-1.5 overflow-hidden rounded-full bg-muted">
          <div
            className="h-full rounded-full bg-primary/70 transition-all"
            style={{ width: `${Math.min(100, Math.max(0, percent))}%` }}
          />
        </div>
      )}
      {target !== undefined && current !== undefined ? (
        <div className="flex justify-between text-[11px] text-muted-foreground">
          <span>Current {current}</span>
          <span>Target {target}</span>
        </div>
      ) : null}
    </div>
  )
}

export function DistributionBar({
  label,
  segments,
}: {
  label: string
  segments: Array<{ id: string; count: number; max: number }>
}) {
  return (
    <div className="space-y-2">
      {label ? <p className="text-xs font-medium">{label}</p> : null}
      <div className="space-y-1.5">
        {segments.map((segment) => (
          <div key={segment.id} className="flex items-center gap-2 text-[11px]">
            <span className="w-6 shrink-0 text-muted-foreground">{segment.id}</span>
            <div className="h-2 flex-1 overflow-hidden rounded-full bg-muted">
              <div
                className="h-full rounded-full bg-primary/70"
                style={{
                  width: `${Math.min(100, (segment.count / Math.max(segment.max, 1)) * 100)}%`,
                }}
              />
            </div>
            <span className="w-4 shrink-0 text-right tabular-nums">{segment.count}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
