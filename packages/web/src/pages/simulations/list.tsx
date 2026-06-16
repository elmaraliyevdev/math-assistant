import { Link } from '@tanstack/react-router'
import { Plus, RefreshCw } from 'lucide-react'
import { useQueries } from '@tanstack/react-query'
import { useMemo, useState } from 'react'

import { ConfirmDialog } from '@/components/ui/confirm-dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useMe } from '@/features/auth/use-auth'
import { gamesApi } from '@/features/games/api/games-api'
import { gameKeys, useGames } from '@/features/games/hooks/use-games'
import {
  SimulationTable,
  SimulationTableEmpty,
  SimulationTableError,
} from '@/features/simulations/components'
import { useSimulationTableRows } from '@/features/simulations/hooks/use-simulation-table-rows'
import {
  useCancelSimulation,
  useSimulations,
} from '@/features/simulations/hooks/use-simulations'
import type { SimulationTableRow } from '@/features/simulations/types'
import { useDebouncedValue } from '@/hooks/use-debounced-value'
import { getErrorMessage } from '@/services/api'

const PAGE_SIZE = 10
const STATUS_OPTIONS = [
  { value: 'all', label: 'All statuses' },
  { value: 'pending', label: 'Pending' },
  { value: 'running', label: 'Running' },
  { value: 'completed', label: 'Completed' },
  { value: 'failed', label: 'Failed' },
  { value: 'cancelled', label: 'Cancelled' },
]

export function SimulationsListPage() {
  const [page, setPage] = useState(1)
  const [status, setStatus] = useState('all')
  const [organizationId, setOrganizationId] = useState('all')
  const [gameVersionId, setGameVersionId] = useState('all')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [search, setSearch] = useState('')
  const debouncedSearch = useDebouncedValue(search)
  const [cancelTarget, setCancelTarget] = useState<SimulationTableRow | null>(
    null,
  )

  const { data: me } = useMe()
  const games = useGames({ page: 1, pageSize: 100 })
  const simulations = useSimulations({
    page,
    pageSize: PAGE_SIZE,
    status: status === 'all' ? undefined : status,
    gameVersionId: gameVersionId === 'all' ? undefined : gameVersionId,
  })

  const enrichedRows = useSimulationTableRows(
    simulations.data?.items,
    games.data?.items,
    me?.organizations,
  )

  const versionQueries = useQueries({
    queries: (games.data?.items ?? []).map((game) => ({
      queryKey: gameKeys.versions(game.id),
      queryFn: () => gamesApi.listVersions(game.id),
      staleTime: 60_000,
    })),
  })

  const versionOptions = useMemo(() => {
    const options: Array<{ id: string; label: string }> = []
    ;(games.data?.items ?? []).forEach((game, index) => {
      for (const version of versionQueries[index]?.data ?? []) {
        options.push({
          id: version.id,
          label: `${game.name} v${version.version}`,
        })
      }
    })
    return options
  }, [games.data?.items, versionQueries])

  const filteredRows = useMemo(() => {
    const query = debouncedSearch.trim().toLowerCase()

    return enrichedRows.filter((row) => {
      if (organizationId !== 'all') {
        const orgName =
          me?.organizations.find((org) => org.organizationId === organizationId)
            ?.organizationName ?? organizationId
        if (row.organizationName !== orgName) {
          return false
        }
      }

      if (dateFrom) {
        const from = new Date(dateFrom).getTime()
        if (new Date(row.createdAt).getTime() < from) {
          return false
        }
      }

      if (dateTo) {
        const to = new Date(dateTo).getTime() + 86_400_000 - 1
        if (new Date(row.createdAt).getTime() > to) {
          return false
        }
      }

      if (!query) {
        return true
      }

      return (
        row.id.toLowerCase().includes(query) ||
        row.gameName.toLowerCase().includes(query)
      )
    })
  }, [dateFrom, dateTo, debouncedSearch, enrichedRows, me?.organizations, organizationId])

  const cancelSimulation = useCancelSimulation(cancelTarget?.id ?? '')
  const totalPages = simulations.data
    ? Math.ceil(simulations.data.total / PAGE_SIZE)
    : 0
  const hasFilters =
    status !== 'all' ||
    organizationId !== 'all' ||
    gameVersionId !== 'all' ||
    Boolean(dateFrom) ||
    Boolean(dateTo) ||
    Boolean(debouncedSearch)

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Simulations</h2>
          <p className="text-muted-foreground">
            Run and monitor mathematical simulations.
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => simulations.refetch()}
            disabled={simulations.isFetching}
          >
            <RefreshCw
              className={`h-4 w-4 ${simulations.isFetching ? 'animate-spin' : ''}`}
            />
            Refresh
          </Button>
          <Button asChild variant="outline">
            <Link to="/simulations/compare">Compare simulations</Link>
          </Button>
          <Button asChild>
            <Link to="/simulations/create">
              <Plus className="h-4 w-4" />
              New simulation
            </Link>
          </Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <div className="space-y-2">
          <Label htmlFor="sim-search">Search</Label>
          <Input
            id="sim-search"
            placeholder="Simulation ID or game name…"
            value={search}
            onChange={(event) => {
              setSearch(event.target.value)
              setPage(1)
            }}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="sim-status">Status</Label>
          <Select
            value={status}
            onValueChange={(value) => {
              setStatus(value)
              setPage(1)
            }}
          >
            <SelectTrigger id="sim-status">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {STATUS_OPTIONS.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label htmlFor="sim-org">Organization</Label>
          <Select
            value={organizationId}
            onValueChange={(value) => {
              setOrganizationId(value)
              setPage(1)
            }}
          >
            <SelectTrigger id="sim-org">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All organizations</SelectItem>
              {(me?.organizations ?? []).map((org) => (
                <SelectItem key={org.organizationId} value={org.organizationId}>
                  {org.organizationName}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label htmlFor="sim-version-filter">Game version</Label>
          <Select
            value={gameVersionId}
            onValueChange={(value) => {
              setGameVersionId(value)
              setPage(1)
            }}
          >
            <SelectTrigger id="sim-version-filter">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All versions</SelectItem>
              {versionOptions.map((option) => (
                <SelectItem key={option.id} value={option.id}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label htmlFor="sim-date-from">From</Label>
          <Input
            id="sim-date-from"
            type="date"
            value={dateFrom}
            onChange={(event) => {
              setDateFrom(event.target.value)
              setPage(1)
            }}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="sim-date-to">To</Label>
          <Input
            id="sim-date-to"
            type="date"
            value={dateTo}
            onChange={(event) => {
              setDateTo(event.target.value)
              setPage(1)
            }}
          />
        </div>
      </div>

      {simulations.isError && (
        <SimulationTableError message={getErrorMessage(simulations.error)} />
      )}

      {!simulations.isError && (
        <SimulationTable
          rows={filteredRows}
          loading={simulations.isLoading}
          cancellingId={
            cancelSimulation.isPending ? cancelTarget?.id ?? null : null
          }
          onCancel={setCancelTarget}
        />
      )}

      {!simulations.isLoading &&
        !simulations.isError &&
        filteredRows.length === 0 && (
          <SimulationTableEmpty hasFilters={hasFilters} />
        )}

      {simulations.data && simulations.data.total > PAGE_SIZE && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Page {page} of {totalPages} · {simulations.data.total} simulations
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page <= 1}
              onClick={() => setPage((current) => current - 1)}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={page >= totalPages}
              onClick={() => setPage((current) => current + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      )}

      <ConfirmDialog
        open={Boolean(cancelTarget)}
        onOpenChange={(open) => !open && setCancelTarget(null)}
        title="Cancel simulation"
        description="Stop this simulation? Spins already completed will be kept."
        confirmLabel="Cancel simulation"
        destructive
        loading={cancelSimulation.isPending}
        onConfirm={() => {
          if (cancelTarget) {
            cancelSimulation.mutate(undefined, {
              onSuccess: () => setCancelTarget(null),
            })
          }
        }}
      />
    </div>
  )
}
