import { cn, formatPercent } from '@/lib/utils'

export function RtpDeviationCell({
  rtp,
  deviation,
}: {
  rtp: number | null
  deviation: number | null
}) {
  if (rtp == null) {
    return <span className="text-muted-foreground">—</span>
  }

  const positive = deviation != null && deviation > 0
  const negative = deviation != null && deviation < 0
  const neutral = deviation == null || deviation === 0

  return (
    <div className="flex flex-col gap-0.5">
      <div className="flex items-center gap-2">
        <span className="font-medium tabular-nums">{formatPercent(rtp)}</span>
        {!neutral && (
          <span
            className={cn(
              'h-1.5 w-1.5 rounded-full',
              positive && 'bg-emerald-500',
              negative && 'bg-red-500',
            )}
            aria-hidden
          />
        )}
      </div>
      {deviation != null && deviation !== 0 && (
        <span
          className={cn(
            'text-xs tabular-nums',
            positive && 'text-emerald-600 dark:text-emerald-400',
            negative && 'text-red-600 dark:text-red-400',
          )}
        >
          {positive ? '+' : ''}
          {formatPercent(deviation)}
        </span>
      )}
    </div>
  )
}
