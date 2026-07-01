import { useGeneratorStudio } from '@/features/reel-studio/generator/context/generator-context'
import { cn } from '@/lib/utils'

function healthLabel(score: number): string {
  if (score >= 95) return 'Production ready'
  if (score >= 80) return 'Good'
  if (score >= 60) return 'Fair'
  return 'Needs attention'
}

function healthColor(score: number): string {
  if (score >= 95) return 'text-emerald-500'
  if (score >= 80) return 'text-foreground'
  if (score >= 60) return 'text-amber-500'
  return 'text-red-500'
}

export function DesignHealthContent() {
  const { designHealth } = useGeneratorStudio()
  const topRecommendation = designHealth.recommendations[0]
  const hasIssues = designHealth.metrics.some((metric) => metric.status !== 'pass')

  return (
    <div className="space-y-4">
      <div className="flex items-baseline gap-4">
        <p className={cn('text-4xl font-semibold tabular-nums', healthColor(designHealth.overallScore))}>
          {designHealth.overallScore}
        </p>
        <p className="text-sm font-medium text-muted-foreground">
          {healthLabel(designHealth.overallScore)}
        </p>
      </div>

      {hasIssues && topRecommendation ? (
        <div className="rounded-lg bg-muted/40 p-4">
          <p className="text-xs font-medium text-muted-foreground">Recommendation</p>
          <p className="mt-2 text-sm">{topRecommendation}</p>
        </div>
      ) : null}

      {hasIssues ? (
        <ul className="space-y-2 text-sm text-muted-foreground">
          {designHealth.metrics
            .filter((metric) => metric.status !== 'pass')
            .slice(0, 4)
            .map((metric) => (
              <li key={metric.id} className="flex justify-between gap-4">
                <span>{metric.label}</span>
                <span className="tabular-nums">{Math.round(metric.score)}</span>
              </li>
            ))}
        </ul>
      ) : null}
    </div>
  )
}

/** @deprecated Use DesignHealthContent inside DesignInspector accordion */
export function DesignHealthPanel() {
  return <DesignHealthContent />
}
