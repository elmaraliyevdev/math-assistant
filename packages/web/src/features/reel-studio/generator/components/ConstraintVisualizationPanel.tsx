import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useConstraintStudio } from '@/features/reel-studio/constraints/context/constraint-studio-context'
import { useReelStudio } from '@/features/reel-studio/context/reel-studio-context'

function renderDistanceVisual(symbolId: string, reelSymbols: string[], minDistance: number): string {
  const chars = reelSymbols.map((id) => (id === symbolId ? symbolId[0] ?? 'S' : '.'))
  const indices = reelSymbols
    .map((id, index) => (id === symbolId ? index : -1))
    .filter((index) => index >= 0)
  let violation = false
  for (let i = 0; i < indices.length - 1; i += 1) {
    const gap = indices[i + 1]! - indices[i]! - 1
    if (gap < minDistance) {
      violation = true
      break
    }
  }
  return `${chars.join('')}${violation ? '  Violation' : ''}`
}

export function ConstraintVisualizationPanel() {
  const { document } = useReelStudio()
  const { constraintDocument, validation, setFocusedViolation } = useConstraintStudio()
  const distanceRules = constraintDocument.constraints.filter(
    (rule) => rule.enabled && rule.type === 'min_distance',
  )
  const reelSet = document.reelSets[document.activeReelSetId]
  if (!reelSet || distanceRules.length === 0) {
    return null
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">Constraint visualization</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {distanceRules.map((rule) => {
          const reel = reelSet.reels.find((item) => item.reelIndex === (rule.reelIndex ?? 0))
          if (!reel) {
            return null
          }
          const visual = renderDistanceVisual(rule.targetId, reel.symbols, rule.value)
          const result = validation.results.find((item) => item.constraintId === rule.id)
          return (
            <button
              key={rule.id}
              type="button"
              className="w-full rounded-md border p-3 text-left"
              onClick={() => result && setFocusedViolation(result)}
            >
              <p className="text-sm font-medium">{rule.targetId}</p>
              <pre className="mt-2 overflow-x-auto font-mono text-xs">{visual}</pre>
              <p className="mt-2 text-xs text-muted-foreground">
                Expected &gt;= {rule.value} symbols apart
                {result && result.status !== 'pass' ? ` · Found ${result.actual}` : ''}
              </p>
            </button>
          )
        })}
      </CardContent>
    </Card>
  )
}
