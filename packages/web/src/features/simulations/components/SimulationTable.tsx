import { useNavigate } from '@tanstack/react-router'
import { Link } from '@tanstack/react-router'

import { EmptyState } from '@/components/empty-state'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { RtpDeviationCell } from '@/features/simulations/components/RtpDeviationCell'
import { SimulationStatusBadge } from '@/features/simulations/components/SimulationStatusBadge'
import type { SimulationTableRow } from '@/features/simulations/types'
import { formatDurationMs } from '@/features/simulations/utils/workbench'
import { simulationDurationMs } from '@/features/simulations/utils/health-score'
import { cn, formatDate, formatNumber } from '@/lib/utils'

interface SimulationTableProps {
  rows: SimulationTableRow[]
  loading?: boolean
}

export function SimulationTable({ rows, loading }: SimulationTableProps) {
  const navigate = useNavigate()

  if (loading) {
    return (
      <div className="space-y-2 rounded-xl border border-border/40 bg-card/30 p-2">
        {Array.from({ length: 6 }).map((_, index) => (
          <Skeleton key={index} className="h-14 w-full rounded-lg" />
        ))}
      </div>
    )
  }

  return (
    <div className="overflow-hidden rounded-xl border border-border/40">
      <Table>
        <TableHeader>
          <TableRow className="hover:bg-transparent">
            <TableHead>Simulation</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="text-right">Spins</TableHead>
            <TableHead>Observed RTP</TableHead>
            <TableHead>Duration</TableHead>
            <TableHead className="text-right">Created</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row) => {
            const duration = simulationDurationMs(row.createdAt, row.completedAt)

            return (
              <TableRow
                key={row.id}
                className={cn(
                  'cursor-pointer transition-colors',
                  'hover:bg-muted/50',
                )}
                onClick={() =>
                  navigate({
                    to: '/simulations/$simulationId',
                    params: { simulationId: row.id },
                  })
                }
              >
                <TableCell>
                  <div className="min-w-0">
                    <p className="truncate font-medium">{row.gameName}</p>
                    <p className="truncate font-mono text-xs text-muted-foreground">
                      {row.id.slice(0, 8)}…
                      {row.versionNumber != null ? ` · v${row.versionNumber}` : ''}
                    </p>
                  </div>
                </TableCell>
                <TableCell>
                  <SimulationStatusBadge status={row.status} />
                </TableCell>
                <TableCell className="text-right tabular-nums">
                  {formatNumber(row.spinCount)}
                </TableCell>
                <TableCell>
                  <RtpDeviationCell rtp={row.rtp} deviation={row.rtpDeviation} />
                </TableCell>
                <TableCell className="text-sm text-muted-foreground">
                  {formatDurationMs(duration)}
                </TableCell>
                <TableCell className="text-right text-sm text-muted-foreground">
                  {formatDate(row.createdAt)}
                </TableCell>
              </TableRow>
            )
          })}
        </TableBody>
      </Table>
    </div>
  )
}

export function SimulationTableEmpty({
  hasFilters,
}: {
  hasFilters?: boolean
}) {
  return (
    <EmptyState
      title={hasFilters ? 'No results' : 'No simulations yet'}
      description={
        hasFilters
          ? 'Try adjusting your search or filters.'
          : 'Run your first simulation to validate RTP, volatility, and feature balance.'
      }
      actions={
        !hasFilters ? (
          <>
            <Button asChild>
              <Link to="/simulations/create">New simulation</Link>
            </Button>
            <Button variant="outline" asChild>
              <Link to="/games">View games</Link>
            </Button>
          </>
        ) : undefined
      }
    />
  )
}

export function SimulationTableError({ message }: { message: string }) {
  return (
    <div className="rounded-xl border border-destructive/30 bg-destructive/5 p-8 text-center">
      <p className="font-medium text-destructive">Failed to load simulations</p>
      <p className="mt-1 text-sm text-muted-foreground">{message}</p>
    </div>
  )
}
