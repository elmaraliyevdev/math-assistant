import type { DragEndEvent, DragStartEvent } from '@dnd-kit/core'

import type { StudioSymbol } from '@/features/reel-studio/types'

export function resolveDragOverlayLabel(
  event: DragStartEvent,
  symbols: Record<string, StudioSymbol>,
): string | null {
  const data = event.active.data.current as { symbolId?: string } | undefined
  const symbolId = data?.symbolId
  if (!symbolId) {
    return null
  }
  const symbol = symbols[symbolId]
  return symbol?.displayName ?? symbolId
}

export function resolveDragEndIds(event: DragEndEvent): {
  activeId: string
  overId: string | null
} {
  return {
    activeId: String(event.active.id),
    overId: event.over ? String(event.over.id) : null,
  }
}
