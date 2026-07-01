import { cn } from '@/lib/utils'
import type { GameTemplate } from '@/features/game-templates/types'

function difficultyStars(features: string[]): string {
  const count = Math.min(5, Math.max(1, Math.ceil(features.length / 2)))
  return '★'.repeat(count) + '☆'.repeat(5 - count)
}

interface TemplateSelectorProps {
  templates: GameTemplate[]
  selectedId?: string
  onSelect: (template: GameTemplate) => void
}

export function TemplateSelector({
  templates,
  selectedId,
  onSelect,
}: TemplateSelectorProps) {
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {templates.map((template) => (
        <button
          key={template.id}
          type="button"
          onClick={() => onSelect(template)}
          className={cn(
            'rounded-2xl border p-4 text-left transition-all duration-200 hover:bg-muted/30',
            selectedId === template.id &&
              'border-primary/50 bg-primary/5 ring-1 ring-primary/30',
          )}
        >
          <p className="text-2xl">🎰</p>
          <p className="mt-2 font-semibold">{template.name}</p>
          <p className="mt-1 text-xs text-muted-foreground line-clamp-2">
            {template.description}
          </p>
          <p className="mt-2 text-xs text-amber-600 dark:text-amber-400">
            {difficultyStars(template.features)}
          </p>
          {template.features.length > 0 ? (
            <p className="mt-2 text-[11px] text-muted-foreground">
              {template.features.slice(0, 4).join(' · ')}
            </p>
          ) : null}
        </button>
      ))}
    </div>
  )
}
