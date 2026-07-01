import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useConstraintStudio } from '@/features/reel-studio/constraints/context/constraint-studio-context'
import { ReelStatisticsPanel } from '@/features/reel-studio/components/ReelStatisticsPanel'

export function AdvancedStatisticsPanel() {
  const { advancedStats } = useConstraintStudio()

  return (
    <div className="space-y-4">
      <ReelStatisticsPanel />
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Advanced metrics</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-xs">
          <Metric label="Entropy" value={advancedStats.entropy.toFixed(3)} />
          <Metric label="Duplicate %" value={`${advancedStats.duplicatePercent.toFixed(1)}%`} />
          <div>
            <p className="mb-1 font-medium">Longest streaks</p>
            <ul className="space-y-0.5 text-muted-foreground">
              {Object.entries(advancedStats.longestStreaks).map(([symbolId, streak]) => (
                <li key={symbolId}>
                  {symbolId}: {streak}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <p className="mb-1 font-medium">Group frequencies</p>
            <ul className="space-y-0.5 text-muted-foreground">
              {Object.entries(advancedStats.groupFrequencies).map(([groupId, count]) => (
                <li key={groupId}>
                  {groupId}: {count}
                </li>
              ))}
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-2">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  )
}
