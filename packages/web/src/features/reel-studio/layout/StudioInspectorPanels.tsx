import { Link } from '@tanstack/react-router'
import { Bot, Sparkles } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useReelStudioDocument } from '@/features/reel-studio/context/reel-studio-context'
import { useStudioCanvas } from '@/features/reel-studio/layout/studio-canvas-context'
import { symbolTypeBadgeClass } from '@/features/reel-studio/lib/symbol-colors'
import type { SymbolType } from '@/features/reel-studio/types'
import { cn } from '@/lib/utils'

const AI_ACTIONS = [
  'Why is RTP low?',
  'Suggest reel improvements',
  'Reduce variance',
  'Explain this warning',
  'Generate better strip',
]

export function SymbolInspector() {
  const document = useReelStudioDocument()
  const { selectedSlot } = useStudioCanvas()

  if (!selectedSlot) {
    return (
      <div className="border-b border-border/20 px-4 py-3 text-xs text-muted-foreground">
        Select a symbol on the canvas to inspect properties.
      </div>
    )
  }

  const reelSet = document.reelSets[document.activeReelSetId]
  const reel = reelSet?.reels[selectedSlot.reelIndex]
  const symbolId = reel?.symbols[selectedSlot.symbolIndex]
  const symbol = symbolId ? document.symbols[symbolId] : undefined

  if (!symbol || !symbolId) {
    return null
  }

  const occurrences =
    reelSet?.reels.reduce((count, strip) => {
      return count + strip.symbols.filter((id) => id === symbolId).length
    }, 0) ?? 0

  const total =
    reelSet?.reels.reduce((sum, strip) => sum + strip.symbols.length, 0) ?? 1
  const frequency = total > 0 ? (occurrences / total) * 100 : 0

  return (
    <div className="border-b border-border/20 px-4 py-3">
      <p className="mb-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">
        Inspector
      </p>
      <div className="space-y-3">
        <div>
          <p className="text-sm font-semibold">{symbol.displayName ?? symbolId}</p>
          <span
            className={cn(
              'mt-1 inline-flex rounded px-1.5 py-0.5 text-[10px] font-medium uppercase',
              symbolTypeBadgeClass(symbol.type),
            )}
          >
            {symbol.type}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div>
            <p className="text-muted-foreground">Frequency</p>
            <p className="font-medium tabular-nums">{frequency.toFixed(1)}%</p>
          </div>
          <div>
            <p className="text-muted-foreground">Count</p>
            <p className="font-medium tabular-nums">{occurrences}</p>
          </div>
          <div>
            <p className="text-muted-foreground">Reel</p>
            <p className="font-medium">R{selectedSlot.reelIndex + 1}</p>
          </div>
          <div>
            <p className="text-muted-foreground">Position</p>
            <p className="font-medium">{selectedSlot.symbolIndex + 1}</p>
          </div>
        </div>
        <div className="space-y-1.5">
          <Label className="text-xs">Type</Label>
          <Select value={symbol.type} disabled>
            <SelectTrigger className="h-8 text-xs">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {(['regular', 'wild', 'scatter', 'bonus'] as SymbolType[]).map((type) => (
                <SelectItem key={type} value={type}>
                  {type}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="rounded-md border border-dashed p-3 text-center text-xs text-muted-foreground">
          Symbol preview
        </div>
      </div>
    </div>
  )
}

export function StudioAiCopilot({
  gameId,
  versionId,
}: {
  gameId: string
  versionId: string
}) {
  return (
    <div className="flex h-full flex-col px-4 py-4">
      <div className="mb-4 flex items-center gap-2">
        <Bot className="h-5 w-5 text-primary" />
        <h3 className="font-semibold">AI Copilot</h3>
      </div>
      <p className="mb-4 text-sm text-muted-foreground">
        Ask about reel balance, RTP, volatility, and constraint warnings — without leaving
        the editor.
      </p>
      <ul className="space-y-2">
        {AI_ACTIONS.map((action) => (
          <li key={action}>
            <Button variant="outline" size="sm" className="h-auto w-full justify-start py-2 text-left" asChild>
              <Link
                to="/assistant"
                search={{
                  prompt: `${action} (game ${gameId}, version ${versionId})`,
                }}
              >
                <Sparkles className="mr-2 h-3.5 w-3.5 shrink-0 text-primary" />
                {action}
              </Link>
            </Button>
          </li>
        ))}
      </ul>
    </div>
  )
}
