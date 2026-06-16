interface RtpGaugeChartProps {
  label: string
  value: number | null
  max?: number
}

export function RtpGaugeChart({ label, value, max = 100 }: RtpGaugeChartProps) {
  const safeValue = value ?? 0
  const ratio = Math.min(Math.max(safeValue / max, 0), 1)
  const angle = ratio * 180
  const radians = (Math.PI * (180 - angle)) / 180
  const needleX = 100 + Math.cos(radians) * 70
  const needleY = 100 - Math.sin(radians) * 70

  return (
    <div className="flex flex-col items-center gap-2">
      <svg viewBox="0 0 200 120" className="h-28 w-full max-w-xs">
        <path
          d="M 30 100 A 70 70 0 0 1 170 100"
          fill="none"
          stroke="hsl(var(--muted))"
          strokeWidth="12"
          strokeLinecap="round"
        />
        <path
          d="M 30 100 A 70 70 0 0 1 170 100"
          fill="none"
          stroke="hsl(var(--primary))"
          strokeWidth="12"
          strokeLinecap="round"
          pathLength={1}
          strokeDasharray={`${ratio} 1`}
        />
        <line
          x1="100"
          y1="100"
          x2={needleX}
          y2={needleY}
          stroke="hsl(var(--foreground))"
          strokeWidth="3"
          strokeLinecap="round"
        />
        <circle cx="100" cy="100" r="5" fill="hsl(var(--foreground))" />
      </svg>
      <div className="text-center">
        <p className="text-xs uppercase tracking-wide text-muted-foreground">
          {label}
        </p>
        <p className="text-lg font-semibold">
          {value === null ? '—' : `${value.toFixed(2)}%`}
        </p>
      </div>
    </div>
  )
}
