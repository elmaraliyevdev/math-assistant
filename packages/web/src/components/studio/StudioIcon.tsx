import type { LucideIcon } from 'lucide-react'

import { cn } from '@/lib/utils'

/** Consistent, readable icon sizing for the design studio */
export function StudioIcon({
  icon: Icon,
  className,
  size = 'md',
}: {
  icon: LucideIcon
  className?: string
  size?: 'md' | 'lg'
}) {
  return (
    <Icon
      className={cn(
        'shrink-0 text-foreground/90',
        size === 'lg' ? 'h-[22px] w-[22px]' : 'h-5 w-5',
        className,
      )}
      strokeWidth={2.25}
      aria-hidden
    />
  )
}
