import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

export type StatusTone =
  | 'default'
  | 'primary'
  | 'success'
  | 'warning'
  | 'destructive'
  | 'muted'

const TONE_STYLES: Record<StatusTone, string> = {
  default: 'bg-secondary text-secondary-foreground hover:bg-secondary',
  primary: 'bg-primary/10 text-primary hover:bg-primary/10',
  success: 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 hover:bg-emerald-500/10',
  warning: 'bg-amber-500/10 text-amber-800 dark:text-amber-300 hover:bg-amber-500/10',
  destructive: 'bg-destructive/10 text-destructive hover:bg-destructive/10',
  muted: 'bg-muted text-muted-foreground hover:bg-muted',
}

export function StatusBadge({
  label,
  tone = 'default',
  className,
}: {
  label: string
  tone?: StatusTone
  className?: string
}) {
  return (
    <Badge
      variant="secondary"
      className={cn('rounded-full border-0 font-medium', TONE_STYLES[tone], className)}
    >
      {label}
    </Badge>
  )
}

/** Map project/game status strings to design-system tones */
export function toneForProjectStatus(
  status: string,
): StatusTone {
  switch (status) {
    case 'ready':
      return 'success'
    case 'certified':
      return 'primary'
    case 'simulating':
      return 'primary'
    case 'review':
      return 'warning'
    case 'needs_attention':
      return 'destructive'
    case 'draft':
      return 'muted'
    default:
      return 'default'
  }
}
