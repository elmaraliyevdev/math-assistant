import type { GroundedCitation } from '@/types/api'

interface CitationPanelProps {
  citations: GroundedCitation[]
}

export function CitationPanel({ citations }: CitationPanelProps) {
  if (citations.length === 0) {
    return null
  }

  return (
    <div className="rounded-md border bg-muted/30 p-3">
      <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        Grounded citations
      </p>
      <ul className="space-y-2 text-sm">
        {citations.map((citation) => (
          <li key={`${citation.source}-${citation.path}`} className="flex flex-col">
            <span className="font-medium">{citation.label}</span>
            <span className="text-muted-foreground">
              {citation.source}.{citation.path}
              {citation.value !== undefined && citation.value !== null
                ? ` = ${citation.value}`
                : ''}
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}
