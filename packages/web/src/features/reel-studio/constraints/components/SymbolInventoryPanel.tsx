import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { symbolTypeBadgeClass } from '@/features/reel-studio/lib/symbol-colors'
import { useConstraintStudio } from '@/features/reel-studio/constraints/context/constraint-studio-context'
import { useReelStudio } from '@/features/reel-studio/context/reel-studio-context'

export function SymbolInventoryPanel() {
  const { document } = useReelStudio()
  const { constraintDocument, updateInventoryCount, updateInventoryTotal } = useConstraintStudio()
  const reelSet = document.reelSets[document.activeReelSetId]
  const reels = reelSet?.reels ?? []

  const symbols = Object.values(document.symbols).sort((a, b) => a.id.localeCompare(b.id))

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">Symbol inventory</CardTitle>
      </CardHeader>
      <CardContent className="overflow-x-auto">
        <table className="w-full min-w-[520px] text-xs">
          <thead>
            <tr className="border-b text-left text-muted-foreground">
              <th className="py-1 pr-2">Symbol</th>
              <th className="py-1 pr-2">Type</th>
              <th className="py-1 pr-2">Total</th>
              {reels.map((reel) => (
                <th key={reel.reelIndex} className="py-1 px-1 text-center">
                  R{reel.reelIndex + 1}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {symbols.map((symbol) => {
              const entry = constraintDocument.inventory[symbol.id]
              const actualTotal = reels.reduce(
                (sum, reel) => sum + reel.symbols.filter((id) => id === symbol.id).length,
                0,
              )
              return (
                <tr key={symbol.id} className="border-b border-muted/50">
                  <td className="py-1 pr-2 font-medium">{symbol.displayName ?? symbol.id}</td>
                  <td className="py-1 pr-2">
                    <Badge className={symbolTypeBadgeClass(symbol.type)} variant="secondary">
                      {symbol.type}
                    </Badge>
                  </td>
                  <td className="py-1 pr-2">
                    <div className="flex items-center gap-1">
                      <Input
                        className="h-7 w-14 px-1 text-xs"
                        type="number"
                        min={0}
                        value={entry?.totalTarget ?? 0}
                        onChange={(event) =>
                          updateInventoryTotal(symbol.id, Number(event.target.value))
                        }
                      />
                      <span className="text-muted-foreground">/ {actualTotal}</span>
                    </div>
                  </td>
                  {reels.map((reel) => {
                    const actual = reel.symbols.filter((id) => id === symbol.id).length
                    const target = entry?.reelCounts[String(reel.reelIndex)] ?? 0
                    const mismatch = target > 0 && target !== actual
                    return (
                      <td key={reel.reelIndex} className="px-1 py-1 text-center">
                        <Input
                          className={`mx-auto h-7 w-12 px-1 text-center text-xs ${mismatch ? 'border-amber-500' : ''}`}
                          type="number"
                          min={0}
                          value={target}
                          onChange={(event) =>
                            updateInventoryCount(
                              symbol.id,
                              reel.reelIndex,
                              Number(event.target.value),
                            )
                          }
                        />
                        <div className="text-[10px] text-muted-foreground">{actual}</div>
                      </td>
                    )
                  })}
                </tr>
              )
            })}
          </tbody>
        </table>
      </CardContent>
    </Card>
  )
}
