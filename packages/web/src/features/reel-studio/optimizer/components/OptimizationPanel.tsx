import { Star, Zap } from 'lucide-react'

import { CollapsibleSection } from '@/components/studio/CollapsibleSection'
import { Button } from '@/components/ui/button'
import { useOptimizerStudio } from '@/features/reel-studio/optimizer/context/optimizer-context'
import { cn } from '@/lib/utils'

function confidenceStars(confidence: number): number {
  if (confidence >= 90) return 5
  if (confidence >= 75) return 4
  if (confidence >= 55) return 3
  if (confidence >= 35) return 2
  return 1
}

function StarRating({ count }: { count: number }) {
  return (
    <span className="inline-flex gap-0.5 text-amber-500">
      {Array.from({ length: 5 }, (_, index) => (
        <Star
          key={index}
          className={cn('h-3 w-3', index < count ? 'fill-current' : 'text-muted-foreground/30')}
        />
      ))}
    </span>
  )
}

export function OptimizationPanel() {
  const {
    proposals,
    output,
    previewProposal,
    isOptimizing,
    preview,
    applyProposal,
    rejectProposalById,
    optimizeTop,
  } = useOptimizerStudio()

  return (
    <CollapsibleSection
      title="Suggestions"
      subtitle={
        proposals.length > 0
          ? `${proposals.length} ranked improvements`
          : 'Design looks healthy'
      }
      defaultOpen
      badge={
        <span className="text-xs text-muted-foreground tabular-nums">
          {output.currentHealth} health
        </span>
      }
    >
      <div className="space-y-3">
        {proposals.length === 0 ? (
          <div className="rounded-lg bg-muted/20 px-3 py-4 text-center">
            <p className="text-sm font-medium">No optimization suggestions</p>
            <p className="mt-1 text-xs text-muted-foreground">
              Your design already satisfies all active goals. Try changing volatility or adding
              additional constraints.
            </p>
            <Button
              type="button"
              size="sm"
              variant="secondary"
              className="mt-3"
              disabled={isOptimizing}
              onClick={() => optimizeTop(5)}
            >
              <Zap className="h-3.5 w-3.5" />
              Scan for improvements
            </Button>
          </div>
        ) : (
          <>
            {proposals.slice(0, 6).map((proposal) => {
              const selected = previewProposal?.id === proposal.id
              const stars = confidenceStars(proposal.confidence)
              return (
                <div
                  key={proposal.id}
                  className={cn(
                    'studio-suggestion space-y-2',
                    selected && 'ring-primary/50 bg-primary/5',
                  )}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <StarRating count={stars} />
                      <p className="mt-1 text-sm font-medium">{proposal.title}</p>
                    </div>
                    <span className="shrink-0 text-xs font-semibold text-emerald-600 dark:text-emerald-400">
                      +{proposal.healthGain} Health
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground">{proposal.description}</p>
                  <p className="text-[11px] text-muted-foreground">
                    Confidence {proposal.confidence}% · Risk {proposal.estimatedRisk}
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    <Button
                      type="button"
                      size="sm"
                      className="h-7"
                      onClick={() => applyProposal(proposal.id)}
                    >
                      Apply
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="ghost"
                      className="h-7"
                      onClick={() => preview(selected ? null : proposal.id)}
                    >
                      {selected ? 'Clear preview' : 'Preview'}
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="ghost"
                      className="h-7"
                      onClick={() => rejectProposalById(proposal.id)}
                    >
                      Dismiss
                    </Button>
                  </div>
                </div>
              )
            })}
          </>
        )}
      </div>
    </CollapsibleSection>
  )
}
