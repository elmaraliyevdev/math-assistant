import { Link, useSearch } from '@tanstack/react-router'
import { Download } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'

import { Button } from '@/components/ui/button'
import { EmptyState } from '@/components/empty-state'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { ComparisonDeltaSummary } from '@/features/workbench/components/ComparisonDeltaSummary'
import { SimulationComparisonWorkbench } from '@/features/simulations/components/SimulationComparisonWorkbench'
import { useSimulationCompare, useSimulations } from '@/features/simulations/hooks/use-simulations'
import {
  deleteComparisonSession,
  listComparisonSessions,
  saveComparisonSession,
} from '@/features/workbench/comparison-sessions'
import { exportsApi } from '@/services/exports'
import { getErrorMessage } from '@/services/api'
import { toast } from '@/lib/toast'

export function SimulationsComparePage() {
  const search = useSearch({ strict: false }) as { ids?: string }
  const initialIds = useMemo(
    () => search.ids?.split(',').filter(Boolean) ?? [],
    [search.ids],
  )

  const simulations = useSimulations({ page: 1, pageSize: 100, status: 'completed' })
  const [selectedIds, setSelectedIds] = useState<string[]>(initialIds)
  const [compareIds, setCompareIds] = useState<string[]>(initialIds)
  const [sessionName, setSessionName] = useState('')
  const [sessions, setSessions] = useState(() => listComparisonSessions())
  const compare = useSimulationCompare(compareIds, compareIds.length >= 2)

  useEffect(() => {
    if (initialIds.length >= 2) {
      setCompareIds(initialIds)
      setSelectedIds(initialIds)
    }
  }, [initialIds])

  const completedItems = useMemo(
    () => (simulations.data?.items ?? []).filter((item) => item.status === 'completed'),
    [simulations.data?.items],
  )

  function toggleSelection(simulationId: string, checked: boolean) {
    setSelectedIds((current) => {
      if (checked) {
        if (current.includes(simulationId) || current.length >= 5) {
          return current
        }
        return [...current, simulationId]
      }
      return current.filter((id) => id !== simulationId)
    })
  }

  async function handleExportPdf() {
    if (compareIds.length < 2) return
    try {
      await exportsApi.downloadComparison(compareIds, 'pdf')
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
    anchor.download = `comparison-${compareIds.join('-')}.json`
    anchor.click()
    URL.revokeObjectURL(url)
  }

  function handleSaveSession() {
    if (!sessionName.trim() || compareIds.length < 2) return
    const saved = saveComparisonSession({
      name: sessionName.trim(),
      simulationIds: compareIds,
      snapshot: compare.data,
    })
    setSessions(listComparisonSessions())
    setSessionName('')
    toast.success(`Saved session "${saved.name}"`)
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Compare simulations</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Select 2–5 completed simulations to compare mathematics side by side.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            variant="outline"
            onClick={handleExportPdf}
            disabled={compareIds.length < 2}
          >
            <Download className="h-4 w-4" />
            Export PDF
          </Button>
          <Button
            variant="outline"
            onClick={handleExportJson}
            disabled={!compare.data}
          >
            Export JSON
          </Button>
          <Button
            onClick={() => setCompareIds([...selectedIds])}
            disabled={selectedIds.length < 2 || selectedIds.length > 5}
          >
            Compare selected ({selectedIds.length})
          </Button>
        </div>
      </div>

      {compare.data && (
        <Card>
          <CardHeader>
            <CardTitle>Save comparison session</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            <Input
              className="max-w-sm"
              placeholder="Session name"
              value={sessionName}
              onChange={(event) => setSessionName(event.target.value)}
            />
            <Button onClick={handleSaveSession} disabled={!sessionName.trim()}>
              Save session
            </Button>
          </CardContent>
        </Card>
      )}

      {sessions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Saved sessions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {sessions.map((session) => (
              <div
                key={session.id}
                className="flex flex-wrap items-center justify-between gap-2 rounded-md border p-3"
              >
                <div>
                  <p className="font-medium">{session.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {session.simulationIds.length} simulations ·{' '}
                    {new Date(session.savedAt).toLocaleString()}
                  </p>
                </div>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setSelectedIds(session.simulationIds)
                      setCompareIds(session.simulationIds)
                    }}
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
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Select completed simulations</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {completedItems.length === 0 && (
            <EmptyState
              title="No completed simulations to compare"
              description="Run at least two simulations to completion, then return here to compare RTP, volatility, and exposure side by side."
              actions={
                <>
                  <Button asChild>
                    <Link to="/simulations/create">Create simulation</Link>
                  </Button>
                  <Button variant="outline" asChild>
                    <Link to="/simulations">View simulations</Link>
                  </Button>
                </>
              }
            />
          )}
          {completedItems.map((simulation) => {
            const checked = selectedIds.includes(simulation.id)
            return (
              <label
                key={simulation.id}
                className="flex cursor-pointer items-start gap-3 rounded-lg border p-3 hover:bg-muted/40"
              >
                <input
                  type="checkbox"
                  className="mt-1"
                  checked={checked}
                  onChange={(event) =>
                    toggleSelection(simulation.id, event.target.checked)
                  }
                  disabled={!checked && selectedIds.length >= 5}
                />
                <div className="min-w-0 flex-1">
                  <p className="font-mono text-xs text-muted-foreground">
                    {simulation.id}
                  </p>
                  <p className="text-sm">
                    {simulation.spinCount.toLocaleString()} spins ·{' '}
                    {simulation.completedAt
                      ? new Date(simulation.completedAt).toLocaleString()
                      : 'completed'}
                  </p>
                </div>
              </label>
            )
          })}
          <p className="text-xs text-muted-foreground">
            {selectedIds.length}/5 selected
          </p>
        </CardContent>
      </Card>

      {compareIds.length >= 2 && compare.isLoading && (
        <p className="text-sm text-muted-foreground">Loading comparison…</p>
      )}

      {compare.isError && (
        <div className="rounded-lg border border-destructive/40 bg-destructive/5 p-4 text-sm text-destructive">
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
  )
}
