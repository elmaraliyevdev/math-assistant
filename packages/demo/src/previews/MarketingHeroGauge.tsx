import { useMemo } from 'react'

interface MarketingHeroGaugeProps {
  label: string
  value: number
  max?: number
  className?: string
}

/** Large RTP gauge for marketing previews — needle tracks animated value. */
export function MarketingHeroGauge({
  label,
  value,
  max = 100,
  className,
}: MarketingHeroGaugeProps) {
  const ratio = useMemo(
    () => Math.min(Math.max(value / max, 0), 1),
    [max, value],
  )
  const angle = ratio * 180
  const radians = (Math.PI * (180 - angle)) / 180
  const needleX = 100 + Math.cos(radians) * 70
  const needleY = 100 - Math.sin(radians) * 70

  return (
    <div className={className}>
      <svg
        viewBox="0 0 200 120"
        className="demo-math-hero-gauge__svg"
        role="img"
        aria-label={`${label} ${value.toFixed(2)} percent`}
      >
        <path
          d="M 30 100 A 70 70 0 0 1 170 100"
          fill="none"
          stroke="var(--muted)"
          strokeWidth="10"
          strokeLinecap="round"
          opacity="0.35"
        />
        <path
          d="M 30 100 A 70 70 0 0 1 170 100"
          fill="none"
          stroke="var(--primary)"
          strokeWidth="10"
          strokeLinecap="round"
          pathLength={1}
          strokeDasharray={`${ratio} 1`}
          className="demo-math-hero-gauge__arc"
        />
        <line
          x1="100"
          y1="100"
          x2={needleX}
          y2={needleY}
          stroke="var(--foreground)"
          strokeWidth="2.5"
          strokeLinecap="round"
          className="demo-math-hero-gauge__needle"
        />
        <circle cx="100" cy="100" r="4" fill="var(--foreground)" />
      </svg>
      <p className="demo-math-hero-gauge__label">{label}</p>
      <p className="demo-math-hero-gauge__value">{value.toFixed(2)}%</p>
    </div>
  )
}
