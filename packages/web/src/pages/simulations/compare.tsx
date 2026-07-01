import { Link, useSearch } from '@tanstack/react-router'
import { Download } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'

import { PageHeader, PageLayout, PageSection } from '@/components/design-system'
import { Button } from '@/components/ui/button'
import { EmptyState } from '@/components/empty-state'
import { Input } from '@/components/ui/input'
import { SimulationComparePreview } from '@/features/simulations/components/compare/SimulationComparePreview'
import { SimulationComparisonWorkbench } from '@/features/simulations/components/SimulationComparisonWorkbench'
import { SimulationStatusBadge } from '@/features/simulations/components/SimulationStatusBadge'
import { useSimulationCompare, useSimulations } from '@/features/simulations/hooks/use-simulations'
import { ComparisonDeltaSummary } from '@/features/workbench/components/ComparisonDeltaSummary'
import {
  deleteComparisonSession,
  listComparisonSessions,
  saveComparisonSession,
} from '@/features/workbench/comparison-sessions'
import { exportsApi } from '@/services/exports'
import { getErrorMessage } from '@/services/api'
import { toast } from '@/lib/toast'
import { cn, formatNumber } from '@/lib/utils'

export function SimulationsComparePage() {
  const search = useSearch({ strict: false }) as { ids?: string }
  const initialIds = useMemo(
    () => search.ids?.split(',').filter(Boolean) ?? [],
    [search.ids],
  )

  const simulations = useSimulations({ page: 1, pageSize: 100, status: 'completed' })
  const [selectedIds, setSelectedIds] = useState<string[]>(initialIds)
  const [sessionName, setSessionName] = useState('')
  const [sessions, setSessions] = useState(() => listComparisonSessions())
  const compare = useSimulationCompare(selectedIds, selectedIds.length >= 2)

  useEffect(() => {
    if (initialIds.length >= 2) {
      setSelectedIds(initialIds)
    }
  }, [initialIds])

  const completedItems = useMemo(
    () => (simulations.data?.items ?? []).filter((item) => item.status === 'completed'),
    [simulations.data?.items],
  )

  function toggleSelection(simulationId: string) {
    setSelectedIds((current) => {
      if (current.includes(simulationId)) {
        return current.filter((id) => id !== simulationId)
      }
      if (current.length >= 5) return current
      return [...current, simulationId]
    })
  }

  async function handleExportPdf() {
    if (selectedIds.length < 2) return
    try {
      await exportsApi.downloadComparison(selectedIds, 'pdf')
    } catch (error) {
      toast.error(getErrorMessage(error))
    }
  }

  function handleExportJson() {
    if (!compare.data) return
    const blob = new Blob([JSON.stringify(compare.data, null, 2)], {
      type: 'application/json',
    })
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = `comparison-${selectedIds.join('-')}.json`
    anchor.click()
    URL.revokeObjectURL(url)
  }

  function handleSaveSession() {
    if (!sessionName.trim() || selectedIds.length < 2 || !compare.data) return
    const saved = saveComparisonSession({
      name: sessionName.trim(),
      simulationIds: selectedIds,
      snapshot: compare.data,
    })
    setSessions(listComparisonSessions())
    setSessionName('')
    toast.success(`Saved session "${saved.name}"`)
  }

  return (
    <PageLayout fullWidth>
      <PageHeader
        title="Compare simulations"
        description="Select runs to compare RTP, volatility, and feature balance side by side."
        actions={
          <>
            <Button
              variant="outline"
              size="sm"
              onClick={handleExportPdf}
              disabled={selectedIds.length < 2}
            >
              <Download className="h-4 w-4" />
              Export PDF
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleExportJson}
              disabled={!compare.data}
            >
              Export JSON
            </Button>
          </>
        }
      />

      <PageSection>
        <div className="grid gap-6 xl:grid-cols-[360px_minmax(0,1fr)]">
          <aside className="space-y-4">
            <div className="rounded-xl border border-border/40 bg-card/30 p-4">
              <div className="flex items-center justify-between">
                <h2 className="font-medium">Simulations</h2>
                <span className="text-xs text-muted-foreground">
                  {selectedIds.length}/5
                </span>
              </div>
              <p className="mt-1 text-sm text-muted-foreground">
                Select 2–5 completed simulations.
              </p>
              <div className="mt-4 max-h-[28rem] space-y-2 overflow-y-auto">
                {completedItems.length === 0 && (
                  <EmptyState
                    title="No completed simulations"
                    description="Run at least two simulations to completion before comparing."
                    actions={
                      <Button asChild size="sm">
                        <Link to="/simulations/create">Create simulation</Link>
                      </Button>
                    }
                  />
                )}
                {completedItems.map((simulation) => {
                  const selected = selectedIds.includes(simulation.id)
                  return (
                    <button
                      key={simulation.id}
                      type="button"
                      onClick={() => toggleSelection(simulation.id)}
                      className={cn(
                        'w-full rounded-lg border px-3 py-3 text-left transition-colors',
                        selected
                          ? 'border-primary/40 bg-primary/5'
                          : 'border-border/40 hover:bg-muted/40',
                      )}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="min-w-0">
                          <p className="truncate font-mono text-xs text-muted-foreground">
                            {simulation.id.slice(0, 8)}…
                          </p>
                          <p className="mt-1 text-sm">
                            {formatNumber(simulation.spinCount)} spins
                          </p>
                        </div>
                        <SimulationStatusBadge status={simulation.status} />
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>

            {compare.data && (
              <div className="rounded-xl border border-border/40 p-4">
                <p className="text-sm font-medium">Save session</p>
                <div className="mt-3 flex gap-2">
                  <Input
                    placeholder="Session name"
                    value={sessionName}
                    onChange={(event) => setSessionName(event.target.value)}
                  />
                  <Button
                    size="sm"
                    onClick={handleSaveSession}
                    disabled={!sessionName.trim()}
                  >
                    Save
                  </Button>
                </div>
              </div>
            )}

            {sessions.length > 0 && (
              <div className="rounded-xl border border-border/40 p-4">
                <p className="text-sm font-medium">Saved sessions</p>
                <div className="mt-3 space-y-2">
                  {sessions.map((session) => (
                    <div
                      key={session.id}
                      className="flex items-center justify-between gap-2 rounded-lg border border-border/40 px-3 py-2"
                    >
                      <div className="min-w-0">
                        <p className="truncate text-sm font-medium">{session.name}</p>
                        <p className="text-xs text-muted-foreground">
                          {session.simulationIds.length} runs
                        </p>
                      </div>
                      <div className="flex gap-1">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => setSelectedIds(session.simulationIds)}
                        >
                          Load
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => {
                            deleteComparisonSession(session.id)
                            setSessions(listComparisonSessions())
                          }}
                        >
                          Delete
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </aside>

          <div className="space-y-6">
            <SimulationComparePreview
              data={compare.data}
              loading={compare.isLoading && selectedIds.length >= 2}
            />

            {compare.isError && (
              <div className="rounded-xl border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive">
                {getErrorMessage(compare.error)}
              </div>
            )}

            {compare.data && (
              <>
                <ComparisonDeltaSummary data={compare.data} />
                <SimulationComparisonWorkbench data={compare.data} />
              </>
            )}
          </div>
        </div>
      </PageSection>
    </PageLayout>
  )
}
