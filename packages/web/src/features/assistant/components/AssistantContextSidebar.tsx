import { Link } from '@tanstack/react-router'

import { EmptyState } from '@/components/empty-state'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { AssistantContextState, AssistantMode } from '@/features/assistant/types'
import { formatPercent } from '@/lib/utils'

export function AssistantContextSidebar({
  context,
  onChange,
  games,
  versions,
  completedSimulations,
  gameName,
  versionNumber,
  observedRtp,
  targetRtp,
  healthScore,
  certificationLabel,
}: {
  context: AssistantContextState
  onChange: (patch: Partial<AssistantContextState>) => void
  games: Array<{ id: string; name: string }>
  versions: Array<{ id: string; version: number }>
  completedSimulations: Array<{ id: string; spinCount: number }>
  gameName?: string
  versionNumber?: number | null
  observedRtp?: number | null
  targetRtp?: number | null
  healthScore?: number | null
  certificationLabel?: string | null
}) {
  const needsGames = context.mode === 'game-version' && games.length === 0
  const needsSimulations =
    (context.mode === 'simulation' || context.mode === 'compare') &&
    completedSimulations.length === 0

  return (
    <aside className="flex h-full min-h-0 flex-col border-l border-border/40 bg-muted/10">
      <div className="border-b border-border/40 px-4 py-3">
        <h2 className="text-sm font-medium">Current context</h2>
        <p className="text-xs text-muted-foreground">Adjust scope without leaving chat</p>
      </div>
      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        <div className="space-y-2">
          <Label>Assistant mode</Label>
          <Select
            value={context.mode}
            onValueChange={(value) => onChange({ mode: value as AssistantMode })}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="simulation">Simulation analysis</SelectItem>
              <SelectItem value="compare">Simulation comparison</SelectItem>
              <SelectItem value="game-version">Game design</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {needsGames && (
          <EmptyState
            title="No games"
            description="Create a game to analyze mathematical design."
            actions={
              <Button size="sm" asChild>
                <Link to="/games/create">Create game</Link>
              </Button>
            }
          />
        )}

        {needsSimulations && (
          <EmptyState
            title="No completed simulations"
            description="Run a simulation before analysis."
            actions={
              <Button size="sm" asChild>
                <Link to="/simulations/create">New simulation</Link>
              </Button>
            }
          />
        )}

        {context.mode === 'game-version' && !needsGames && (
          <>
            <div className="space-y-2">
              <Label>Game</Label>
              <Select
                value={context.gameId}
                onValueChange={(value) =>
                  onChange({ gameId: value, gameVersionId: '' })
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select game" />
                </SelectTrigger>
                <SelectContent>
                  {games.map((game) => (
                    <SelectItem key={game.id} value={game.id}>
                      {game.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Version</Label>
              <Select
                value={context.gameVersionId}
                onValueChange={(value) => onChange({ gameVersionId: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select version" />
                </SelectTrigger>
                <SelectContent>
                  {versions.map((version) => (
                    <SelectItem key={version.id} value={version.id}>
                      v{version.version}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </>
        )}

        {context.mode === 'simulation' && !needsSimulations && (
          <div className="space-y-2">
            <Label>Simulation</Label>
            <Select
              value={context.simulationId}
              onValueChange={(value) => onChange({ simulationId: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select simulation" />
              </SelectTrigger>
              <SelectContent>
                {completedSimulations.map((simulation) => (
                  <SelectItem key={simulation.id} value={simulation.id}>
                    {simulation.id.slice(0, 8)} · {simulation.spinCount.toLocaleString()} spins
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        {context.mode === 'compare' && !needsSimulations && (
          <div className="space-y-2">
            <Label>Compare simulations</Label>
            <div className="max-h-40 space-y-2 overflow-y-auto rounded-lg border border-border/40 p-2">
              {completedSimulations.map((simulation) => {
                const checked = context.compareIds.includes(simulation.id)
                return (
                  <label
                    key={simulation.id}
                    className="flex items-center gap-2 text-sm"
                  >
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => {
                        const next = checked
                          ? context.compareIds.filter((id) => id !== simulation.id)
                          : [...context.compareIds, simulation.id].slice(0, 5)
                        onChange({ compareIds: next })
                      }}
                    />
                    {simulation.id.slice(0, 8)}
                  </label>
                )
              })}
            </div>
          </div>
        )}

        <ContextSummary
          gameName={gameName}
          versionNumber={versionNumber}
          observedRtp={observedRtp}
          targetRtp={targetRtp}
          healthScore={healthScore}
          certificationLabel={certificationLabel}
        />
      </div>
    </aside>
  )
}

function ContextSummary({
  gameName,
  versionNumber,
  observedRtp,
  targetRtp,
  healthScore,
  certificationLabel,
}: {
  gameName?: string
  versionNumber?: number | null
  observedRtp?: number | null
  targetRtp?: number | null
  healthScore?: number | null
  certificationLabel?: string | null
}) {
  if (!gameName && healthScore == null && observedRtp == null) return null

  return (
    <div className="rounded-xl border border-border/40 bg-background/60 p-3 text-sm">
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
        Snapshot
      </p>
      <dl className="mt-3 space-y-2">
        {gameName ? (
          <div className="flex justify-between gap-2">
            <dt className="text-muted-foreground">Game</dt>
            <dd className="truncate font-medium">{gameName}</dd>
          </div>
        ) : null}
        {versionNumber != null ? (
          <div className="flex justify-between gap-2">
            <dt className="text-muted-foreground">Version</dt>
            <dd className="font-medium">v{versionNumber}</dd>
          </div>
        ) : null}
        {healthScore != null ? (
          <div className="flex justify-between gap-2">
            <dt className="text-muted-foreground">Health</dt>
            <dd className="font-medium tabular-nums">{healthScore}</dd>
          </div>
        ) : null}
        {observedRtp != null ? (
          <div className="flex justify-between gap-2">
            <dt className="text-muted-foreground">Observed RTP</dt>
            <dd className="font-medium tabular-nums">{formatPercent(observedRtp)}</dd>
          </div>
        ) : null}
        {targetRtp != null ? (
          <div className="flex justify-between gap-2">
            <dt className="text-muted-foreground">Target RTP</dt>
            <dd className="font-medium tabular-nums">{formatPercent(targetRtp)}</dd>
          </div>
        ) : null}
        {certificationLabel ? (
          <div className="flex justify-between gap-2">
            <dt className="text-muted-foreground">Certification</dt>
            <dd className="font-medium">{certificationLabel}</dd>
          </div>
        ) : null}
      </dl>
    </div>
  )
}
