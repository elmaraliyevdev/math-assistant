import { CollapsibleSection } from '@/components/studio/CollapsibleSection'
import { DistributionBar } from '@/components/studio/VisualMeter'
import { useConstraintStudio } from '@/features/reel-studio/constraints/context/constraint-studio-context'
import { useReelStudio } from '@/features/reel-studio/context/reel-studio-context'
import { cn } from '@/lib/utils'

export function SymbolInventoryDashboard() {
  const { document } = useReelStudio()
  const { constraintDocument } = useConstraintStudio()
  const reelSet = document.reelSets[document.activeReelSetId]
  if (!reelSet) {
    return null
  }

  const entries = Object.values(constraintDocument.inventory)
  if (entries.length === 0) {
    return null
  }

  const maxPerReel = Math.max(
    ...entries.flatMap((entry) =>
      reelSet.reels.map(
        (reel) => reel.symbols.filter((id) => id === entry.symbolId).length,
      ),
    ),
    1,
  )

  return (
    <CollapsibleSection title="Symbol inventory" subtitle={`${entries.length} tracked symbols`}>
      <div className="space-y-4">
        {entries.map((entry) => {
          const perReel = reelSet.reels.map(
            (reel) => reel.symbols.filter((id) => id === entry.symbolId).length,
          )
          const current = perReel.reduce((sum, count) => sum + count, 0)
          const target = entry.totalTarget
          const diff = current - target
          const balanced = diff === 0

          return (
            <div key={entry.symbolId} className="space-y-2">
              <div className="flex items-center justify-between gap-2">
                <span className="text-sm font-medium">{entry.symbolId}</span>
                <span
                  className={cn(
                    'text-xs tabular-nums',
                    balanced
                      ? 'text-emerald-600 dark:text-emerald-400'
                      : Math.abs(diff) <= 2
                        ? 'text-amber-600'
                        : 'text-red-600',
                  )}
                >
                  {diff > 0 ? '+' : ''}
                  {diff}
                </span>
              </div>
              <DistributionBar
                label=""
                segments={perReel.map((count, index) => ({
                  id: `R${index + 1}`,
                  count,
                  max: maxPerReel,
                }))}
              />
              <div className="flex gap-3 text-[11px] text-muted-foreground">
                <span>Current {current}</span>
                <span>Target {target}</span>
              </div>
            </div>
          )
        })}
      </div>
    </CollapsibleSection>
  )
}
