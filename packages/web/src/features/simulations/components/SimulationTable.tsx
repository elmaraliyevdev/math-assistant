import { Link } from '@tanstack/react-router'
import { Ban, Eye } from 'lucide-react'

import { Badge, statusBadgeVariant } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { EmptyState } from '@/components/empty-state'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import type { SimulationTableRow } from '@/features/simulations/types'
import { formatDate, formatNumber, formatPercent } from '@/lib/utils'

interface SimulationTableProps {
  rows: SimulationTableRow[]
  loading?: boolean
  onCancel: (row: SimulationTableRow) => void
  cancellingId?: string | null
}

export function SimulationTable({
  rows,
  loading,
  onCancel,
  cancellingId,
}: SimulationTableProps) {
  if (loading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 5 }).map((_, index) => (
          <Skeleton key={index} className="h-12 w-full" />
        ))}
      </div>
    )
  }

  return (
    <div className="overflow-x-auto rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Simulation ID</TableHead>
            <TableHead>Game</TableHead>
            <TableHead>Version</TableHead>
            <TableHead>Spins</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>RTP</TableHead>
            <TableHead>Total Bet</TableHead>
            <TableHead>Total Win</TableHead>
            <TableHead>Created</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row) => {
            const canCancel =
              row.status === 'pending' || row.status === 'running'

            return (
              <TableRow key={row.id}>
                <TableCell className="font-mono text-xs">
                  {row.id.slice(0, 8)}…
                </TableCell>
                <TableCell className="font-medium">{row.gameName}</TableCell>
                <TableCell>
                  {row.versionNumber != null ? `v${row.versionNumber}` : '—'}
                </TableCell>
                <TableCell>{formatNumber(row.spinCount)}</TableCell>
                <TableCell>
                  <Badge variant={statusBadgeVariant(row.status)}>
                    {row.status}
                  </Badge>
                </TableCell>
                <TableCell>
                  {row.rtp != null ? formatPercent(row.rtp) : '—'}
                </TableCell>
                <TableCell>
                  {row.totalBetMinorUnits != null
                    ? formatNumber(row.totalBetMinorUnits)
                    : '—'}
                </TableCell>
                <TableCell>
                  {row.totalWinMinorUnits != null
                    ? formatNumber(row.totalWinMinorUnits)
                    : '—'}
                </TableCell>
                <TableCell>{formatDate(row.createdAt)}</TableCell>
                <TableCell>
                  <div className="flex justify-end gap-1">
                    <Button variant="ghost" size="icon" asChild>
                      <Link
                        to="/simulations/$simulationId"
                        params={{ simulationId: row.id }}
                      >
                        <Eye className="h-4 w-4" />
                        <span className="sr-only">View</span>
                      </Link>
                    </Button>
                    {canCancel && (
                      <Button
                        variant="ghost"
                        size="icon"
                        disabled={cancellingId === row.id}
                        onClick={() => onCancel(row)}
                      >
                        <Ban className="h-4 w-4 text-destructive" />
                        <span className="sr-only">Cancel</span>
                      </Button>
                    )}
                  </div>
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
      title="No simulations found"
      description={
        hasFilters
          ? 'Try adjusting your filters or search query.'
          : 'Run your first simulation to validate RTP, volatility, and feature balance.'
      }
      actions={
        !hasFilters ? (
          <>
            <Button asChild>
              <Link to="/simulations/create">Create simulation</Link>
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
    <div className="rounded-lg border border-destructive/40 bg-destructive/5 p-6 text-center">
      <p className="font-medium text-destructive">Failed to load simulations</p>
      <p className="mt-1 text-sm text-muted-foreground">{message}</p>
    </div>
  )
}
