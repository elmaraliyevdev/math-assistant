import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useConstraintStudio } from '@/features/reel-studio/constraints/context/constraint-studio-context'
import { useReelStudio } from '@/features/reel-studio/context/reel-studio-context'
import { useGeneratorStudio } from '@/features/reel-studio/generator/context/generator-context'

function statusLabel(diff: number): { text: string; className: string } {
  if (diff === 0) {
    return { text: 'Balanced', className: 'text-emerald-600' }
  }
  if (Math.abs(diff) <= 2) {
    return { text: 'Warning', className: 'text-amber-600' }
  }
  return { text: 'Imbalanced', className: 'text-red-600' }
}

function DistributionBar({ value, max }: { value: number; max: number }) {
  const width = max > 0 ? Math.round((value / max) * 100) : 0
  return (
    <div className="h-2 flex-1 rounded bg-muted">
      <div className="h-2 rounded bg-primary" style={{ width: `${width}%` }} />
    </div>
  )
}

export function DistributionDashboard() {
  const { document } = useReelStudio()
  const { constraintDocument } = useConstraintStudio()
  const { previewCandidate } = useGeneratorStudio()
  const reelSet = document.reelSets[document.activeReelSetId]
  if (!reelSet) {
    return null
  }

  const distribution =
    previewCandidate?.distribution ??
    reelSet.reels.reduce<Record<string, Record<number, number>>>((acc, reel) => {
      reel.symbols.forEach((symbolId) => {
        acc[symbolId] ??= {}
        acc[symbolId]![reel.reelIndex] = (acc[symbolId]![reel.reelIndex] ?? 0) + 1
      })
      return acc
    }, {})

  const symbolIds = Object.keys(distribution).sort()
  const reelCount = reelSet.reels.length

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">Distribution dashboard</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {symbolIds.map((symbolId) => {
          const perReel = distribution[symbolId] ?? {}
          const current = Object.values(perReel).reduce((sum, value) => sum + value, 0)
          const target = constraintDocument.inventory[symbolId]?.totalTarget ?? current
          const diff = current - target
          const maxBar = Math.max(target, current, ...Object.values(perReel), 1)
          const status = statusLabel(diff)
          return (
            <div key={symbolId} className="space-y-2 rounded-md border p-3">
              <div className="flex items-center justify-between gap-2">
                <p className="text-sm font-medium">{symbolId}</p>
                <span className={`text-xs font-medium ${status.className}`}>{status.text}</span>
              </div>
              {Array.from({ length: reelCount }, (_, reelIndex) => (
                <div key={reelIndex} className="flex items-center gap-2 text-xs">
                  <span className="w-6 shrink-0">R{reelIndex + 1}</span>
                  <DistributionBar value={perReel[reelIndex] ?? 0} max={maxBar} />
                  <span className="w-4 text-right">{perReel[reelIndex] ?? 0}</span>
                </div>
              ))}
              <div className="flex flex-wrap gap-3 text-xs text-muted-foreground">
                <span>Target {target}</span>
                <span>Current {current}</span>
                <span>
                  Difference {diff > 0 ? '+' : ''}
                  {diff}
                </span>
              </div>
            </div>
          )
        })}
      </CardContent>
    </Card>
  )
}
