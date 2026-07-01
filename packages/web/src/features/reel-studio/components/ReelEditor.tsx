import { Sparkles } from 'lucide-react'

import { ReelColumn } from '@/features/reel-studio/components/ReelColumn'
import { useReelStudioDocument } from '@/features/reel-studio/context/reel-studio-context'
import { useStudioCanvas } from '@/features/reel-studio/layout/studio-canvas-context'

function PlaceholderReels() {
  return (
    <div className="flex items-end justify-center gap-6 opacity-[0.12]" aria-hidden>
      {Array.from({ length: 5 }).map((_, reelIndex) => (
        <div key={reelIndex} className="flex w-14 flex-col gap-2">
          <div className="mb-2 h-3 w-8 rounded bg-muted-foreground/30" />
          {Array.from({ length: 3 }).map((__, row) => (
            <div
              key={row}
              className="h-12 rounded-lg border border-dashed border-muted-foreground/40 bg-muted/30"
            />
          ))}
        </div>
      ))}
    </div>
  )
}

function EmptyCanvasHint() {
  return (
    <div
      className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center text-center"
      aria-hidden
    >
      <PlaceholderReels />
      <div className="mt-8 max-w-sm space-y-2">
        <p className="text-base font-medium text-muted-foreground/50">Open a game to begin editing</p>
        <p className="text-sm text-muted-foreground/40">
          Drag symbols from the palette or generate your first reel strip
        </p>
        <p className="mt-3 flex items-center justify-center gap-2 text-xs text-muted-foreground/35">
          <Sparkles className="h-3.5 w-3.5" />
          Space + drag to pan · Scroll to zoom
        </p>
      </div>
    </div>
  )
}

export function ReelEditor() {
  const document = useReelStudioDocument()
  const reelSet = document.reelSets[document.activeReelSetId]
  const { selectedReelIndex, setSelectedReelIndex } = useStudioCanvas()

  if (!reelSet) {
    return (
      <div className="flex h-full min-h-[20rem] items-center justify-center">
        <p className="text-sm text-muted-foreground">No reel set selected</p>
      </div>
    )
  }

  const isEmpty = reelSet.reels.every((reel) => reel.symbols.length === 0)

  return (
    <div className="relative w-full min-w-max">
      {isEmpty ? <EmptyCanvasHint /> : null}
      <div className="flex items-start justify-start gap-8 pb-8">
        {reelSet.reels.map((reel) => (
          <ReelColumn
            key={reel.reelIndex}
            reel={reel}
            selected={selectedReelIndex === reel.reelIndex}
            onSelect={() =>
              setSelectedReelIndex(
                selectedReelIndex === reel.reelIndex ? null : reel.reelIndex,
              )
            }
          />
        ))}
      </div>
    </div>
  )
}
