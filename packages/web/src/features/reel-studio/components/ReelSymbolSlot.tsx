import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { Copy, GripVertical, Trash2 } from 'lucide-react'
import { memo } from 'react'

import { StudioIcon } from '@/components/studio/StudioIcon'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import type { ValidationResultItem } from '@/features/reel-studio/constraints/types'
import { slotId } from '@/features/reel-studio/lib/reel-mutations'
import { symbolTypeBadgeClass } from '@/features/reel-studio/lib/symbol-colors'
import type { StudioSymbol } from '@/features/reel-studio/types'
import { cn } from '@/lib/utils'

interface ReelSymbolSlotProps {
  reelIndex: number
  symbolIndex: number
  symbolId: string
  symbol?: StudioSymbol
  violations?: ValidationResultItem[]
  heatmapIntensity?: { wild: number; scatter: number; violation: number }
  isDiff?: boolean
  isDropTarget?: boolean
  isSelected?: boolean
  onSelect?: () => void
  onRemove: () => void
  onDuplicate: () => void
}

export const ReelSymbolSlot = memo(function ReelSymbolSlot({
  reelIndex,
  symbolIndex,
  symbolId,
  symbol,
  violations = [],
  heatmapIntensity,
  isDiff = false,
  isDropTarget = false,
  isSelected = false,
  onSelect,
  onRemove,
  onDuplicate,
}: ReelSymbolSlotProps) {
  const id = slotId(reelIndex, symbolIndex)
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id,
    data: { reelIndex, symbolIndex, symbolId, source: 'reel' },
  })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  }

  const type = symbol?.type ?? 'regular'
  const label = symbol?.displayName ?? symbolId
  const violationClass = violations.some((item) => item.status === 'error')
    ? 'bg-red-500/10 ring-1 ring-red-500/40'
    : violations.length > 0
      ? 'bg-amber-500/10 ring-1 ring-amber-500/40'
      : ''
  const heatmapClass =
    !violationClass && heatmapIntensity
      ? heatmapIntensity.violation > 0.5
        ? 'ring-2 ring-red-400/50'
        : heatmapIntensity.wild > 0.5
          ? 'ring-2 ring-primary/50'
          : heatmapIntensity.scatter > 0.5
            ? 'ring-2 ring-sky-400/50'
            : ''
      : ''
  const violationTitle = violations.map((item) => item.message).join('; ')

  return (
    <div ref={setNodeRef} style={style}>
      <Card
        title={violationTitle}
        className={cn(
          'group min-h-[44px] cursor-pointer border-0 shadow-sm transition-all duration-150',
          'hover:shadow-md',
          isSelected && 'studio-symbol--selected shadow-md ring-2 ring-primary/50',
          isDragging && 'opacity-40 shadow-lg ring-2 ring-primary/40',
          isDropTarget && !isSelected && 'ring-2 ring-primary/40',
          isDiff && !isSelected && 'outline outline-2 outline-offset-1 outline-primary',
          violationClass,
          heatmapClass,
        )}
        onClick={(event) => {
          event.stopPropagation()
          onSelect?.()
        }}
      >
      <div className="flex items-center gap-3 px-3 py-2.5">
        <button
          type="button"
          className="flex shrink-0 cursor-grab items-center text-foreground/70 transition-colors hover:text-foreground active:cursor-grabbing"
          aria-label={`Drag ${label}`}
          onClick={(event) => event.stopPropagation()}
          {...listeners}
          {...attributes}
        >
          <StudioIcon icon={GripVertical} size="lg" />
        </button>
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-medium">{label}</p>
          <p className={cn('text-xs capitalize text-muted-foreground', symbolTypeBadgeClass(type))}>
            {type}
          </p>
        </div>
        <div className="flex gap-0.5 opacity-0 transition-opacity group-hover:opacity-100">
          <Button
            type="button"
            size="icon"
            variant="ghost"
            className="h-8 w-8"
            aria-label={`Duplicate ${label}`}
            onClick={(event) => {
              event.stopPropagation()
              onDuplicate()
            }}
          >
            <StudioIcon icon={Copy} />
          </Button>
          <Button
            type="button"
            size="icon"
            variant="ghost"
            className="h-8 w-8 text-destructive"
            aria-label={`Remove ${label}`}
            onClick={(event) => {
              event.stopPropagation()
              onRemove()
            }}
          >
            <StudioIcon icon={Trash2} className="text-destructive" />
          </Button>
        </div>
      </div>
    </Card>
    </div>
  )
})
