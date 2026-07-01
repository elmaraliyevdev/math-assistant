import { Link } from '@tanstack/react-router'

import type { GroundedCitation } from '@/types/api'

interface CitationPanelProps {
  citations: GroundedCitation[]
}

function citationHref(citation: GroundedCitation): string | null {
  if (citation.source === 'simulation' && citation.path) {
    return `/simulations/${citation.path}`
  }
  if (citation.source === 'game_version' && citation.path) {
    return `/games`
  }
  return null
}

export function CitationPanel({ citations }: CitationPanelProps) {
  if (citations.length === 0) return null

  return (
    <div className="rounded-xl border border-border/40 bg-muted/20 p-3">
      <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
        Citations
      </p>
      <ul className="space-y-2 text-sm">
        {citations.map((citation) => {
          const href = citationHref(citation)
          return (
            <li key={`${citation.source}-${citation.path}-${citation.label}`}>
              {href ? (
                <Link
                  to={href}
                  className="font-medium text-primary hover:underline"
                >
                  {citation.label}
                </Link>
              ) : (
                <span className="font-medium">{citation.label}</span>
              )}
              <p className="text-xs text-muted-foreground">
                {citation.source}
                {citation.value !== undefined && citation.value !== null
                  ? ` · ${citation.value}`
                  : ''}
              </p>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
