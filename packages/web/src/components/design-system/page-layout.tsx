import type { ReactNode } from 'react'

import { cn } from '@/lib/utils'

/** Standard page shell — max 1400px, centered, 8pt spacing */
export function PageLayout({
  children,
  className,
  fullWidth = false,
}: {
  children: ReactNode
  className?: string
  /** Studio and other canvas views may opt out of max-width */
  fullWidth?: boolean
}) {
  return (
    <div
      className={cn(
        'w-full',
        !fullWidth && 'mx-auto max-w-[1400px]',
        className,
      )}
    >
      {children}
    </div>
  )
}

export function PageHeader({
  title,
  description,
  actions,
  className,
}: {
  title: ReactNode
  description?: ReactNode
  actions?: ReactNode
  className?: string
}) {
  return (
    <header
      className={cn(
        'mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between',
        className,
      )}
    >
      <div className="space-y-2">
        <h1 className="text-4xl font-bold tracking-tight">{title}</h1>
        {description ? (
          <p className="text-sm text-muted-foreground">{description}</p>
        ) : null}
      </div>
      {actions ? <div className="flex shrink-0 flex-wrap gap-2">{actions}</div> : null}
    </header>
  )
}

export function PageToolbar({
  children,
  className,
}: {
  children: ReactNode
  className?: string
}) {
  return (
    <div className={cn('mb-6 flex flex-col gap-4 lg:flex-row lg:items-center', className)}>
      {children}
    </div>
  )
}

export function PageSection({
  children,
  className,
}: {
  children: ReactNode
  className?: string
}) {
  return <section className={cn('mb-8 space-y-4', className)}>{children}</section>
}

export function SectionHeader({
  title,
  description,
  action,
  className,
}: {
  title: string
  description?: string
  action?: ReactNode
  className?: string
}) {
  return (
    <div className={cn('flex items-start justify-between gap-4', className)}>
      <div className="space-y-1">
        <h2 className="text-2xl font-semibold tracking-tight">{title}</h2>
        {description ? (
          <p className="text-sm text-muted-foreground">{description}</p>
        ) : null}
      </div>
      {action}
    </div>
  )
}

export function ActionBar({
  children,
  className,
}: {
  children: ReactNode
  className?: string
}) {
  return (
    <div className={cn('flex flex-wrap items-center gap-2', className)}>{children}</div>
  )
}
