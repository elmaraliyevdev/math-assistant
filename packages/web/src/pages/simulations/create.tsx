import { Link, useSearch } from '@tanstack/react-router'
import { useEffect, useMemo, useState } from 'react'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { gamesApi } from '@/features/games/api/games-api'
import { useGames } from '@/features/games/hooks/use-games'
import { SimulationForm } from '@/features/simulations/components'
import { useCreateSimulation } from '@/features/simulations/hooks/use-simulations'
import type { SimulationFormValues } from '@/features/simulations/schemas/simulation-schemas'

export function SimulationCreatePage() {
  const search = useSearch({ strict: false }) as { gameVersionId?: string }
  const games = useGames({ page: 1, pageSize: 100 })
  const createSimulation = useCreateSimulation()
  const [resolvedGameId, setResolvedGameId] = useState<string | undefined>()

  useEffect(() => {
    if (!search.gameVersionId || !games.data?.items.length) {
      return
    }

    let cancelled = false

    async function resolveGameId() {
      for (const game of games.data?.items ?? []) {
        const versions = await gamesApi.listVersions(game.id)
        if (versions.some((version) => version.id === search.gameVersionId)) {
          if (!cancelled) {
            setResolvedGameId(game.id)
          }
          return
        }
      }
    }

    void resolveGameId()

    return () => {
      cancelled = true
    }
  }, [games.data?.items, search.gameVersionId])

  const defaultValues = useMemo(() => {
    if (!search.gameVersionId) {
      return undefined
    }

    return {
      gameId: resolvedGameId,
      gameVersionId: search.gameVersionId,
    } satisfies Partial<SimulationFormValues>
  }, [resolvedGameId, search.gameVersionId])

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Create simulation</h2>
        <p className="text-muted-foreground">
          Configure spin count, bet size, and seeds for a game version.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Simulation parameters</CardTitle>
        </CardHeader>
        <CardContent>
          <SimulationForm
            key={`${resolvedGameId ?? 'new'}-${search.gameVersionId ?? 'none'}`}
            games={games.data?.items ?? []}
            defaultValues={defaultValues}
            loading={createSimulation.isPending || games.isLoading}
            onSubmit={(values) =>
              createSimulation.mutate({
                gameVersionId: values.gameVersionId,
                spinCount: values.spinCount,
                betMinorUnits: values.betMinorUnits,
                masterSeed: values.masterSeed || undefined,
                eventLogMode: values.eventLogMode,
              })
            }
          />
          <div className="mt-4">
            <Link
              to="/simulations"
              className="text-sm text-muted-foreground underline-offset-4 hover:underline"
            >
              Back to simulations
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
