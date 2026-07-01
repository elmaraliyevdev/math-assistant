import { Link } from '@tanstack/react-router'
import { useMemo, useState } from 'react'

import { PageHeader, PageLayout, PageSection } from '@/components/design-system'
import { Button } from '@/components/ui/button'
import { useMe } from '@/features/auth/use-auth'
import { gamesApi } from '@/features/games/api/games-api'
import { gameKeys, useGames } from '@/features/games/hooks/use-games'
import {
  SimulationListStats,
  SimulationListToolbar,
  SimulationTable,
  SimulationTableEmpty,
  SimulationTableError,
  resolveDateRange,
} from '@/features/simulations/components'
import type { SimulationListFilters } from '@/features/simulations/components'
import { useSimulationListStats } from '@/features/simulations/hooks/use-simulation-list-stats'
import { useSimulationTableRows } from '@/features/simulations/hooks/use-simulation-table-rows'
import { useSimulations } from '@/features/simulations/hooks/use-simulations'
import { useDebouncedValue } from '@/hooks/use-debounced-value'
import { useQueries } from '@tanstack/react-query'
import { getErrorMessage } from '@/services/api'

const PAGE_SIZE = 10

export function SimulationsListPage() {
  const [page, setPage] = useState(1)
  const [filters, setFilters] = useState<SimulationListFilters>({
    search: '',
    status: 'all',
    gameVersionId: 'all',
    organizationId: 'all',
    datePreset: 'all',
    dateFrom: '',
    dateTo: '',
  })
  const debouncedSearch = useDebouncedValue(filters.search)

  const { data: me } = useMe()
  const games = useGames({ page: 1, pageSize: 100 })
  const simulations = useSimulations({
    page,
    pageSize: PAGE_SIZE,
    status: filters.status === 'all' ? undefined : filters.status,
    gameVersionId:
      filters.gameVersionId === 'all' ? undefined : filters.gameVersionId,
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

  const organizationOptions = useMemo(
    () =>
      (me?.organizations ?? []).map((org) => ({
        id: org.organizationId,
        label: org.organizationName,
      })),
    [me?.organizations],
  )

  const dateRange = resolveDateRange(
    filters.datePreset,
    filters.dateFrom,
    filters.dateTo,
  )

  const filteredRows = useMemo(() => {
    const query = debouncedSearch.trim().toLowerCase()

    return enrichedRows.filter((row) => {
      if (filters.organizationId !== 'all') {
        const orgName =
          me?.organizations.find(
            (org) => org.organizationId === filters.organizationId,
          )?.organizationName ?? filters.organizationId
        if (row.organizationName !== orgName) return false
      }

      if (dateRange.from) {
        const from = new Date(dateRange.from).getTime()
        if (new Date(row.createdAt).getTime() < from) return false
      }

      if (dateRange.to) {
        const to = new Date(dateRange.to).getTime() + 86_400_000 - 1
        if (new Date(row.createdAt).getTime() > to) return false
      }

      if (!query) return true

      return (
        row.id.toLowerCase().includes(query) ||
        row.gameName.toLowerCase().includes(query)
      )
    })
  }, [
    dateRange.from,
    dateRange.to,
    debouncedSearch,
    enrichedRows,
    filters.organizationId,
    me?.organizations,
  ])

  const stats = useSimulationListStats(enrichedRows)

  const totalPages = simulations.data
    ? Math.ceil(simulations.data.total / PAGE_SIZE)
    : 0
  const hasFilters =
    filters.status !== 'all' ||
    filters.organizationId !== 'all' ||
    filters.gameVersionId !== 'all' ||
    filters.datePreset !== 'all' ||
    Boolean(debouncedSearch)

  function updateFilters(patch: Partial<SimulationListFilters>) {
    setFilters((current) => ({ ...current, ...patch }))
    setPage(1)
  }

  return (
    <PageLayout>
      <PageHeader
        title="Simulations"
        description="Validate mathematics with confidence"
        actions={
          <Button asChild variant="outline">
            <Link to="/simulations/compare">Compare</Link>
          </Button>
        }
      />

      <PageSection className="space-y-4">
        <SimulationListToolbar
          filters={filters}
          onChange={updateFilters}
          versionOptions={versionOptions}
          organizationOptions={organizationOptions}
          onRefresh={() => simulations.refetch()}
          refreshing={simulations.isFetching}
        />

        <SimulationListStats
          completed={stats.completed}
          running={stats.running}
          failed={stats.failed}
          avgRtp={stats.avgRtp}
          avgDuration={stats.avgDuration}
          loading={stats.isLoading}
        />

        {simulations.isError && (
          <SimulationTableError message={getErrorMessage(simulations.error)} />
        )}

        {!simulations.isError && (
          <SimulationTable rows={filteredRows} loading={simulations.isLoading} />
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
      </PageSection>
    </PageLayout>
  )
}
