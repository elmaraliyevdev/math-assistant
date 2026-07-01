import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { useReelStudio } from '@/features/reel-studio/context/reel-studio-context'

function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`
}

export function ReelStatisticsPanel() {
  const { stats, document } = useReelStudio()
  const symbolMap = document.symbols

  return (
    <Card className="h-full">
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Live statistics</CardTitle>
        <p className="text-xs text-muted-foreground">Reel set: {stats.reelSetId}</p>
      </CardHeader>
      <CardContent className="space-y-4">
        {stats.reels.map((reel) => (
          <div key={reel.reelIndex} className="space-y-2">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium">Reel {reel.reelIndex + 1}</p>
              <Badge variant="outline">{reel.length} symbols</Badge>
            </div>
            {reel.symbols.length === 0 ? (
              <p className="text-xs text-muted-foreground">Empty reel</p>
            ) : (
              <ul className="space-y-1 text-xs">
                {reel.symbols.map((item) => (
                  <li key={item.symbolId} className="flex justify-between gap-2">
                    <span className="truncate">
                      {symbolMap[item.symbolId]?.displayName ?? item.symbolId}
                    </span>
                    <span className="shrink-0 text-muted-foreground">
                      {item.count} ({formatPercent(item.percentage)})
                    </span>
                  </li>
                ))}
              </ul>
            )}
            {reel.duplicateSymbolIds.length > 0 && (
              <p className="text-xs text-amber-700 dark:text-amber-300">
                Duplicates: {reel.duplicateSymbolIds.join(', ')}
              </p>
            )}
            <Separator />
          </div>
        ))}

        <div className="space-y-2">
          <p className="text-sm font-semibold">Totals</p>
          <p className="text-xs text-muted-foreground">
            {stats.totals.totalSymbols} symbols across {stats.reels.length} reels
          </p>
          {stats.totals.symbolCounts.length > 0 && (
            <ul className="space-y-1 text-xs">
              {stats.totals.symbolCounts.map((item) => (
                <li key={item.symbolId} className="flex justify-between gap-2">
                  <span className="truncate">
                    {symbolMap[item.symbolId]?.displayName ?? item.symbolId}
                  </span>
                  <span className="shrink-0 text-muted-foreground">
                    {item.count} ({formatPercent(item.percentage)})
                  </span>
                </li>
              ))}
            </ul>
          )}
          {stats.totals.duplicateSymbolIds.length > 0 && (
            <p className="text-xs text-amber-700 dark:text-amber-300">
              Duplicates: {stats.totals.duplicateSymbolIds.join(', ')}
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
