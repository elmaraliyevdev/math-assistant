import { useState } from 'react'

import { Button } from '@/components/ui/button'
import { useReelStudio } from '@/features/reel-studio/context/reel-studio-context'
import { useGeneratorStudio } from '@/features/reel-studio/generator/context/generator-context'
import { slotId } from '@/features/reel-studio/lib/reel-mutations'

export function SmartSuggestionsContent() {
  const { suggestions } = useGeneratorStudio()
  const { handleDragEnd } = useReelStudio()
  const [dismissed, setDismissed] = useState<Set<string>>(() => new Set())
  const [explained, setExplained] = useState<string | null>(null)

  const visible = suggestions.filter((item) => !dismissed.has(item.id))

  return (
    <div className="space-y-3">
      {visible.map((suggestion) => (
        <div key={suggestion.id} className="space-y-2 rounded-lg bg-muted/30 p-4">
          <p className="text-sm">{suggestion.action}</p>
          {explained === suggestion.id ? (
            <p className="text-xs text-muted-foreground">
              Move {suggestion.symbolId} from Reel {suggestion.fromReel + 1} position{' '}
              {suggestion.fromPosition + 1} to Reel {suggestion.toReel + 1} position{' '}
              {suggestion.toPosition + 1}. Expected:{' '}
              {suggestion.expectedImprovements.join(', ')}.
            </p>
          ) : null}
          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              size="sm"
              onClick={() =>
                handleDragEnd(
                  slotId(suggestion.fromReel, suggestion.fromPosition),
                  slotId(suggestion.toReel, suggestion.toPosition),
                )
              }
            >
              Apply
            </Button>
            <Button
              type="button"
              size="sm"
              variant="ghost"
              onClick={() => setDismissed((current) => new Set(current).add(suggestion.id))}
            >
              Dismiss
            </Button>
            <Button
              type="button"
              size="sm"
              variant="ghost"
              onClick={() =>
                setExplained((current) => (current === suggestion.id ? null : suggestion.id))
              }
            >
              Explain
            </Button>
          </div>
        </div>
      ))}
    </div>
  )
}

/** @deprecated Use SmartSuggestionsContent inside DesignInspector accordion */
export function SmartSuggestionsPanel() {
  return <SmartSuggestionsContent />
}
