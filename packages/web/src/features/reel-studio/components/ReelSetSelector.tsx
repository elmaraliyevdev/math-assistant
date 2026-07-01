import { useReelStudio } from '@/features/reel-studio/context/reel-studio-context'
import { cn } from '@/lib/utils'

function formatReelSetLabel(id: string): string {
  return id
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

export function ReelSetSelector({ variant = 'buttons' }: { variant?: 'buttons' | 'text' }) {
  const { document, setActiveReelSet } = useReelStudio()
  const reelSetIds = Object.keys(document.reelSets)

  if (reelSetIds.length === 0) {
    return null
  }

  if (variant === 'text') {
    const activeLabel = formatReelSetLabel(document.activeReelSetId)

    if (reelSetIds.length === 1) {
      return <p className="text-sm text-muted-foreground">{activeLabel}</p>
    }

    return (
      <div className="flex flex-wrap items-center gap-1 text-sm text-muted-foreground">
        {reelSetIds.map((id, index) => (
          <span key={id} className="inline-flex items-center gap-1">
            {index > 0 ? <span className="text-muted-foreground/50">•</span> : null}
            <button
              type="button"
              onClick={() => setActiveReelSet(id)}
              className={cn(
                'transition-colors hover:text-foreground',
                document.activeReelSetId === id
                  ? 'font-medium text-foreground'
                  : 'text-muted-foreground',
              )}
            >
              {formatReelSetLabel(id)}
            </button>
          </span>
        ))}
      </div>
    )
  }

  if (reelSetIds.length <= 1) {
    return (
      <p className="text-sm text-muted-foreground">
        {formatReelSetLabel(reelSetIds[0] ?? '')}
      </p>
    )
  }

  return (
    <div className="flex flex-wrap gap-1 text-sm">
      {reelSetIds.map((id, index) => (
        <span key={id} className="inline-flex items-center gap-1">
          {index > 0 ? <span className="text-muted-foreground/50">•</span> : null}
          <button
            type="button"
            onClick={() => setActiveReelSet(id)}
            className={cn(
              'transition-colors hover:text-foreground',
              document.activeReelSetId === id
                ? 'font-medium text-foreground'
                : 'text-muted-foreground',
            )}
          >
            {formatReelSetLabel(id)}
          </button>
        </span>
      ))}
    </div>
  )
}
