import { useDraggable } from '@dnd-kit/core'
import { CSS } from '@dnd-kit/utilities'

import { symbolTypeBadgeClass } from '@/features/reel-studio/lib/symbol-colors'
import type { StudioSymbol } from '@/features/reel-studio/types'
import { paletteId } from '@/features/reel-studio/lib/reel-mutations'
import { cn } from '@/lib/utils'

function PaletteSymbol({ symbol }: { symbol: StudioSymbol }) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: paletteId(symbol.id),
    data: { symbolId: symbol.id, source: 'palette' },
  })

  const style = {
    transform: CSS.Translate.toString(transform),
    opacity: isDragging ? 0.5 : 1,
  }

  return (
    <button
      ref={setNodeRef}
      type="button"
      style={style}
      className={cn(
        'flex w-full cursor-grab items-center justify-between gap-2 rounded-lg bg-muted/30 px-3 py-2.5 text-left transition-colors',
        'hover:bg-muted/50 active:cursor-grabbing',
        isDragging && 'ring-2 ring-primary/40',
      )}
      {...listeners}
      {...attributes}
    >
      <div className="min-w-0">
        <p className="truncate text-sm font-medium">{symbol.displayName ?? symbol.id}</p>
        <p className={cn('text-[10px] capitalize', symbolTypeBadgeClass(symbol.type))}>
          {symbol.type}
        </p>
      </div>
    </button>
  )
}

export function SymbolPalette({
  symbols,
}: {
  symbols: Record<string, StudioSymbol>
  compact?: boolean
}) {
  const entries = Object.values(symbols).sort((a, b) => a.id.localeCompare(b.id))

  if (entries.length === 0) {
    return <p className="py-8 text-center text-sm text-muted-foreground">No symbols defined.</p>
  }

  return (
    <div className="space-y-1.5">
      {entries.map((symbol) => (
        <PaletteSymbol key={symbol.id} symbol={symbol} />
      ))}
    </div>
  )
}
