import type { ReactNode } from 'react'

import { cn } from '../lib/cn'

export type DemoSectionProps = {
  eyebrow?: string
  title: string
  description?: string
  children?: ReactNode
  className?: string
  align?: 'left' | 'center'
}

/**
 * Landing-style section wrapper with consistent heading hierarchy.
 */
export function DemoSection({
  eyebrow,
  title,
  description,
  children,
  className,
  align = 'left',
}: DemoSectionProps) {
  const centered = align === 'center'

  return (
    <section className={cn('space-y-6', className)}>
      <div className={cn('max-w-2xl', centered && 'mx-auto text-center')}>
        {eyebrow ? (
          <p className="text-xs font-medium uppercase tracking-wider text-primary">{eyebrow}</p>
        ) : null}
        <h2 className={cn('text-2xl font-bold tracking-tight md:text-3xl', eyebrow && 'mt-2')}>
          {title}
        </h2>
        {description ? (
          <p className="mt-3 text-muted-foreground">{description}</p>
        ) : null}
      </div>
      {children}
    </section>
  )
}
