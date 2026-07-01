import { AlertTriangle } from 'lucide-react'

import { useConstraintStudio } from '@/features/reel-studio/constraints/context/constraint-studio-context'
import { cn } from '@/lib/utils'

export function ValidationSidebar() {
  const { validation, setFocusedViolation } = useConstraintStudio()
  const failing = validation.results.filter((item) => item.status !== 'pass')
  const blocking = failing.filter((item) => item.status === 'error')
  const warnings = failing.filter((item) => item.status === 'warning')
  const productionScore =
    validation.summary.error === 0 && validation.summary.warning === 0
      ? 100
      : Math.max(
          0,
          100 -
            validation.summary.error * 15 -
            validation.summary.warning * 5,
        )
  const isReady = blocking.length === 0

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="studio-metric-label">Production ready</p>
          <p
            className={cn(
              'studio-metric',
              isReady ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600',
            )}
          >
            {Math.round(productionScore)}
          </p>
          <p className="mt-1 text-sm text-muted-foreground">
            {isReady
              ? 'No blocking issues.'
              : `${blocking.length} blocking · ${warnings.length} warnings`}
          </p>
        </div>
        {!isReady ? (
          <AlertTriangle className="h-5 w-5 shrink-0 text-amber-500" />
        ) : null}
      </div>

      {failing.length > 0 ? (
        <div className="space-y-2">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Issues to resolve
          </p>
          {failing.map((item) => (
            <button
              key={`${item.constraintId}-${item.message}`}
              type="button"
              className={cn(
                'w-full rounded-lg p-3 text-left text-xs transition-colors',
                item.status === 'error'
                  ? 'bg-red-500/10 ring-1 ring-red-500/20 hover:bg-red-500/15'
                  : 'bg-amber-500/10 ring-1 ring-amber-500/20 hover:bg-amber-500/15',
              )}
              onClick={() => setFocusedViolation(item)}
            >
              <p className="font-medium">{item.message}</p>
              <p className="mt-0.5 text-muted-foreground">{item.description}</p>
              <p className="mt-1">
                Expected {item.expected} · Found {item.actual}
              </p>
              {item.affectedReels.length > 0 && (
                <p>Reels: {item.affectedReels.map((reel) => reel + 1).join(', ')}</p>
              )}
              {item.suggestedFix ? (
                <p className="mt-1 text-amber-800 dark:text-amber-200">{item.suggestedFix}</p>
              ) : null}
            </button>
          ))}
        </div>
      ) : null}
    </div>
  )
}
