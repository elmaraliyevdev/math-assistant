import type { ReactNode } from 'react'

import { FieldHelp } from '@/features/workbench/components/FieldHelp'
import { GLOSSARY, type GlossaryTermKey } from '@/lib/glossary'

interface GlossaryTermProps {
  term: GlossaryTermKey
  children?: ReactNode
  className?: string
}

export function GlossaryTerm({ term, children, className }: GlossaryTermProps) {
  const entry = GLOSSARY[term]
  return (
    <span className={className ?? 'inline-flex items-center gap-1'}>
      {children ?? entry.label}
      <FieldHelp description={entry.definition} />
    </span>
  )
}
