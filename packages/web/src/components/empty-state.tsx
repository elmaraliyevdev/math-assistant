import type { ReactNode } from 'react'

import { cn } from '@/lib/utils'

interface EmptyStateProps {
  title: string
  description: string
  actions?: ReactNode
  className?: string
}

export function EmptyState({
  title,
  description,
  actions,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        'rounded-lg border border-dashed p-8 text-center sm:p-10',
        className,
      )}
    >
      <p className="text-lg font-medium">{title}</p>
      <p className="mt-2 text-sm text-muted-foreground">{description}</p>
      {actions ? <div className="mt-4 flex flex-wrap justify-center gap-2">{actions}</div> : null}
    </div>
  )
}
