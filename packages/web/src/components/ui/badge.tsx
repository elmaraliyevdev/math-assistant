import { cva, type VariantProps } from 'class-variance-authority'
import type * as React from 'react'

import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-primary text-primary-foreground',
        secondary: 'border-transparent bg-secondary text-secondary-foreground',
        outline: 'text-foreground',
        success: 'border-transparent bg-emerald-600/15 text-emerald-700 dark:text-emerald-300',
        warning: 'border-transparent bg-amber-600/15 text-amber-700 dark:text-amber-300',
        danger: 'border-transparent bg-destructive/15 text-destructive',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
)

export function Badge({
  className,
  variant,
  ...props
}: React.HTMLAttributes<HTMLDivElement> & VariantProps<typeof badgeVariants>) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />
}

export function statusBadgeVariant(status: string) {
  switch (status) {
    case 'completed':
      return 'success' as const
    case 'failed':
    case 'cancelled':
      return 'danger' as const
    case 'running':
    case 'pending':
      return 'warning' as const
    default:
      return 'secondary' as const
  }
}
