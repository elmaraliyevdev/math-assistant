import { useDroppable } from '@dnd-kit/core'
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable'
import { memo, useMemo } from 'react'

import { ReelSymbolSlot } from '@/features/reel-studio/components/ReelSymbolSlot'
import { useReelViolations } from '@/features/reel-studio/constraints/context/reel-violation-context'
import { useGeneratorStudio } from '@/features/reel-studio/generator/context/generator-context'
import { useOptimizerStudio } from '@/features/reel-studio/optimizer/context/optimizer-context'
import { positionKey } from '@/features/reel-studio/constraints/types'
import { useReelStudio } from '@/features/reel-studio/context/reel-studio-context'
import { useStudioCanvas } from '@/features/reel-studio/layout/studio-canvas-context'
import { reelContainerId, slotId } from '@/features/reel-studio/lib/reel-mutations'
import type { StudioReelStrip } from '@/features/reel-studio/types'
import { cn } from '@/lib/utils'

interface ReelColumnProps {
  reel: StudioReelStrip
  selected?: boolean
  onSelect?: () => void
}

export const ReelColumn = memo(function ReelColumn({ reel, selected = false, onSelect }: ReelColumnProps) {
  const { document, removeSymbol, duplicateSymbol } = useReelStudio()
  const { violationsByPosition } = useReelViolations()
  const { heatmapOverlay, diffPositions } = useGeneratorStudio()
  const { previewDiffPositions } = useOptimizerStudio()
  const { activeDropTargetId, selectedSlot, setSelectedSlot } = useStudioCanvas()
  const mergedDiffPositions = useMemo(() => {
    if (previewDiffPositions.size > 0) {
      return previewDiffPositions
    }
    return diffPositions
  }, [diffPositions, previewDiffPositions])
  const containerId = reelContainerId(reel.reelIndex)
  const { setNodeRef, isOver } = useDroppable({
    id: containerId,
    data: { reelIndex: reel.reelIndex },
  })

  const isDropTarget = isOver || activeDropTargetId === containerId

  const sortableIds = reel.symbols.map((_, index) => slotId(reel.reelIndex, index))

  return (
    <div
      data-reel-index={reel.reelIndex}
      className={cn(
        'studio-reel-column transition-all duration-200',
        selected && 'studio-reel-column--selected',
        isDropTarget && 'studio-reel-column--drop-target',
      )}
      onClick={onSelect}
      onKeyDown={(event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          onSelect?.()
        }
      }}
      role="button"
      tabIndex={0}
    >
      <div className="mb-3 flex items-baseline justify-between">
        <p className="text-sm font-medium text-muted-foreground">R{reel.reelIndex + 1}</p>
        <p className="text-xs tabular-nums text-muted-foreground">{reel.symbols.length}</p>
      </div>
      <div
        ref={setNodeRef}
        className={cn(
          'min-h-[280px] space-y-3 rounded-2xl p-3 transition-all duration-150',
          isDropTarget ? 'bg-primary/5 ring-2 ring-primary/30' : 'bg-muted/20',
        )}
      >
        <SortableContext items={sortableIds} strategy={verticalListSortingStrategy}>
          {reel.symbols.map((symbolId, symbolIndex) => {
            const id = slotId(reel.reelIndex, symbolIndex)
            const isSlotDropTarget = activeDropTargetId === id
            return (
              <div key={id} className="relative">
                {isSlotDropTarget ? (
                  <div className="absolute -top-1 left-2 right-2 z-10 h-0.5 rounded-full bg-primary shadow-[0_0_8px] shadow-primary/50" />
                ) : null}
                <ReelSymbolSlot
                  reelIndex={reel.reelIndex}
                  symbolIndex={symbolIndex}
                  symbolId={symbolId}
                  symbol={document.symbols[symbolId]}
                  violations={violationsByPosition[positionKey(reel.reelIndex, symbolIndex)]}
                  heatmapIntensity={heatmapOverlay[positionKey(reel.reelIndex, symbolIndex)]}
                  isDiff={mergedDiffPositions.has(`${reel.reelIndex}:${symbolIndex}`)}
                  isDropTarget={isSlotDropTarget}
                  isSelected={
                    selectedSlot?.reelIndex === reel.reelIndex &&
                    selectedSlot?.symbolIndex === symbolIndex
                  }
                  onSelect={() =>
                    setSelectedSlot(
                      selectedSlot?.reelIndex === reel.reelIndex &&
                        selectedSlot?.symbolIndex === symbolIndex
                        ? null
                        : { reelIndex: reel.reelIndex, symbolIndex },
                    )
                  }
                  onRemove={() => removeSymbol(reel.reelIndex, symbolIndex)}
                  onDuplicate={() => duplicateSymbol(reel.reelIndex, symbolIndex)}
                />
              </div>
            )
          })}
        </SortableContext>
        {reel.symbols.length === 0 && (
          <p className="py-12 text-center text-xs text-muted-foreground">Drop symbols here</p>
        )}
      </div>
    </div>
  )
})
