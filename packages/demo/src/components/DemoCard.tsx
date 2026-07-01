import type { ReactNode } from 'react'

import { cn } from '../lib/cn'

export type DemoCardProps = {
  title?: string
  description?: string
  children?: ReactNode
  className?: string
  headerAction?: ReactNode
  padding?: 'none' | 'sm' | 'md'
}

const paddingClass = {
  none: '',
  sm: 'p-3',
  md: 'p-4',
} as const

/**
 * Generic bordered card for demo content. Uses application design-token class names.
 */
export function DemoCard({
  title,
  description,
  children,
  className,
  headerAction,
  padding = 'md',
}: DemoCardProps) {
  return (
    <div
      className={cn(
        'overflow-hidden rounded-lg border border-border bg-card text-card-foreground shadow-sm',
        className,
      )}
    >
      {(title || description || headerAction) && (
        <div className="flex items-start justify-between gap-3 border-b border-border/60 px-4 py-3">
          <div className="min-w-0">
            {title ? <h3 className="text-sm font-semibold leading-none">{title}</h3> : null}
            {description ? (
              <p className="mt-1 text-xs text-muted-foreground">{description}</p>
            ) : null}
          </div>
          {headerAction ? <div className="shrink-0">{headerAction}</div> : null}
        </div>
      )}
      {children ? <div className={paddingClass[padding]}>{children}</div> : null}
    </div>
  )
}
