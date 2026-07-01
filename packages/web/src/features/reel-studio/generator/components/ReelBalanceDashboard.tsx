import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { runConstraintEngine } from '@/features/reel-studio/constraints/engine'
import { computeAdvancedStatistics } from '@/features/reel-studio/constraints/lib/advanced-statistics'
import { useConstraintStudio } from '@/features/reel-studio/constraints/context/constraint-studio-context'
import { useReelStudio } from '@/features/reel-studio/context/reel-studio-context'

function healthLabel(entropy: number, violations: number): string {
  if (violations > 0) {
    return 'Unhealthy'
  }
  if (entropy >= 2.5) {
    return 'Healthy'
  }
  return 'Warning'
}

export function ReelBalanceDashboard() {
  const { document } = useReelStudio()
  const { constraintDocument } = useConstraintStudio()
  const reelSet = document.reelSets[document.activeReelSetId]
  if (!reelSet) {
    return null
  }

  const validation = runConstraintEngine({
    reelSet,
    symbols: document.symbols,
    constraintDocument,
  })

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">Reel balance</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {reelSet.reels.map((reel) => {
          const miniSet = { id: 'mini', reels: [reel] }
          const stats = computeAdvancedStatistics(
            miniSet,
            document.symbols,
            constraintDocument.groups,
            constraintDocument.edgeWrapping,
          )
          const uniqueSymbols = new Set(reel.symbols).size
          const featureCount = reel.symbols.filter((id) => {
            const type = document.symbols[id]?.type
            return type === 'wild' || type === 'scatter' || type === 'bonus'
          }).length
          const reelViolations = validation.results.filter(
            (item) => item.status !== 'pass' && item.affectedReels.includes(reel.reelIndex),
          ).length
          const entropyScore = Math.round(Math.min(100, stats.entropy * 35))
          const densityScore = Math.round(
            Math.min(100, (uniqueSymbols / Math.max(reel.symbols.length, 1)) * 100),
          )
          const label = healthLabel(stats.entropy, reelViolations)
          return (
            <div key={reel.reelIndex} className="rounded-md border p-3 text-sm">
              <div className="flex items-center justify-between">
                <p className="font-medium">R{reel.reelIndex + 1}</p>
                <span
                  className={
                    label === 'Healthy'
                      ? 'text-emerald-600'
                      : label === 'Warning'
                        ? 'text-amber-600'
                        : 'text-red-600'
                  }
                >
                  {label}
                </span>
              </div>
              <div className="mt-2 grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-muted-foreground">
                <span>Length {reel.symbols.length}</span>
                <span>Unique {uniqueSymbols}</span>
                <span>Entropy {entropyScore}</span>
                <span>Density {densityScore}</span>
                <span>Features {featureCount}</span>
                <span>Violations {reelViolations}</span>
              </div>
            </div>
          )
        })}
      </CardContent>
    </Card>
  )
}
