import type { ReactNode } from 'react'

import { EmptyState as DsEmptyState } from '@/components/design-system/empty-state'

interface EmptyStateProps {
  title: string
  description: string
  actions?: ReactNode
  className?: string
}

/** @deprecated Use `@/components/design-system` EmptyState with icon prop */
export function EmptyState({ title, description, actions, className }: EmptyStateProps) {
  return (
    <DsEmptyState
      title={title}
      description={description}
      action={actions}
      className={className}
    />
  )
}
