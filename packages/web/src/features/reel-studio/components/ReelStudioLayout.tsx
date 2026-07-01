import {
  DndContext,
  DragOverlay,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragStartEvent,
} from '@dnd-kit/core'
import { useState } from 'react'

import { JsonPreviewDrawer } from '@/features/reel-studio/components/JsonPreviewDrawer'
import { ReelEditor } from '@/features/reel-studio/components/ReelEditor'
import { ReelSetSelector } from '@/features/reel-studio/components/ReelSetSelector'
import { ReelStatisticsPanel } from '@/features/reel-studio/components/ReelStatisticsPanel'
import { SymbolPalette } from '@/features/reel-studio/components/SymbolPalette'
import { useReelStudio } from '@/features/reel-studio/context/reel-studio-context'
import {
  resolveDragEndIds,
  resolveDragOverlayLabel,
} from '@/features/reel-studio/lib/drag-events'

export function ReelStudioLayout() {
  const { document, handleDragEnd } = useReelStudio()
  const [activeLabel, setActiveLabel] = useState<string | null>(null)
  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 6 } }))

  const onDragStart = (event: DragStartEvent) => {
    setActiveLabel(resolveDragOverlayLabel(event, document.symbols))
  }

  const onDragEnd = (event: DragEndEvent) => {
    setActiveLabel(null)
    const { activeId, overId } = resolveDragEndIds(event)
    handleDragEnd(activeId, overId)
  }

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragStart={onDragStart}
      onDragEnd={onDragEnd}
    >
      <div className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <ReelSetSelector />
          <JsonPreviewDrawer />
        </div>
        <div className="grid gap-4 xl:grid-cols-[minmax(220px,260px)_1fr_minmax(240px,300px)]">
          <SymbolPalette symbols={document.symbols} />
          <ReelEditor />
          <ReelStatisticsPanel />
        </div>
      </div>
      <DragOverlay>
        {activeLabel ? (
          <div className="rounded-md border bg-background px-3 py-2 text-sm shadow-lg">
            {activeLabel}
          </div>
        ) : null}
      </DragOverlay>
    </DndContext>
  )
}
