import {
  DndContext,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors,
} from '@dnd-kit/core'
import type { ReactNode } from 'react'

/** Minimal DnD shell for reel editor + palette previews. */
export function ReelStudioDndShell({ children }: { children: ReactNode }) {
  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 8 } }))

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter}>
      {children}
    </DndContext>
  )
}
