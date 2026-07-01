import { Check, Clock, Loader2, X } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

const STATUS_STYLES: Record<
  string,
  { label: string; className: string; icon?: 'check' | 'x' | 'loader' | 'clock' }
> = {
  completed: {
    label: 'Completed',
    className: 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400',
    icon: 'check',
  },
  failed: {
    label: 'Failed',
    className: 'bg-destructive/10 text-destructive',
    icon: 'x',
  },
  running: {
    label: 'Running',
    className: 'bg-primary/10 text-primary',
    icon: 'loader',
  },
  pending: {
    label: 'Queued',
    className: 'bg-muted text-muted-foreground',
    icon: 'clock',
  },
  cancelled: {
    label: 'Cancelled',
    className: 'bg-muted text-muted-foreground',
  },
}

export function SimulationStatusBadge({
  status,
  className,
}: {
  status: string
  className?: string
}) {
  const config = STATUS_STYLES[status] ?? {
    label: status,
    className: 'bg-secondary text-secondary-foreground',
  }

  return (
    <Badge
      variant="secondary"
      className={cn(
        'gap-1.5 rounded-full border-0 font-medium capitalize',
        config.className,
        className,
      )}
    >
      {config.icon === 'check' && <Check className="h-3 w-3" />}
      {config.icon === 'x' && <X className="h-3 w-3" />}
      {config.icon === 'loader' && <Loader2 className="h-3 w-3 animate-spin" />}
      {config.icon === 'clock' && <Clock className="h-3 w-3" />}
      {config.label}
    </Badge>
  )
}
