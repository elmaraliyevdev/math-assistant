import { cn } from '@/lib/utils'
import type { GameTemplate } from '@/features/game-templates/types'

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
    <div className="grid gap-2 sm:grid-cols-2">
      {templates.map((template) => (
        <button
          key={template.id}
          type="button"
          onClick={() => onSelect(template)}
          className={cn(
            'rounded-lg border p-3 text-left transition-colors hover:bg-accent',
            selectedId === template.id && 'border-primary bg-accent',
          )}
        >
          <p className="font-medium">{template.name}</p>
          <p className="mt-1 text-xs text-muted-foreground">{template.description}</p>
        </button>
      ))}
    </div>
  )
}
