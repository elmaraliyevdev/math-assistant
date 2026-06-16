import type { ComponentProps } from 'react'

import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface PermissionActionButtonProps extends ComponentProps<typeof Button> {
  allowed: boolean
  disabledReason?: string
}

export function PermissionActionButton({
  allowed,
  disabledReason,
  disabled,
  className,
  title,
  ...props
}: PermissionActionButtonProps) {
  const isDisabled = disabled || !allowed
  const tooltip = !allowed && disabledReason ? disabledReason : title

  return (
    <span
      className={cn('inline-flex', className)}
      title={isDisabled ? tooltip : undefined}
    >
      <Button {...props} disabled={isDisabled} title={undefined} />
    </span>
  )
}
