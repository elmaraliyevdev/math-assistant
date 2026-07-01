import { Link } from '@tanstack/react-router'
import { Filter, Plus, RefreshCw } from 'lucide-react'
import { useState } from 'react'

import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

const STATUS_OPTIONS = [
  { value: 'all', label: 'All statuses' },
  { value: 'pending', label: 'Queued' },
  { value: 'running', label: 'Running' },
  { value: 'completed', label: 'Completed' },
  { value: 'failed', label: 'Failed' },
  { value: 'cancelled', label: 'Cancelled' },
]

const DATE_OPTIONS = [
  { value: 'all', label: 'Any time' },
  { value: '7d', label: 'Last 7 days' },
  { value: '30d', label: 'Last 30 days' },
  { value: '90d', label: 'Last 90 days' },
  { value: 'custom', label: 'Custom range' },
]

export type SimulationListFilters = {
  search: string
  status: string
  gameVersionId: string
  organizationId: string
  datePreset: string
  dateFrom: string
  dateTo: string
}

type SimulationListToolbarProps = {
  filters: SimulationListFilters
  onChange: (patch: Partial<SimulationListFilters>) => void
  versionOptions: Array<{ id: string; label: string }>
  organizationOptions: Array<{ id: string; label: string }>
  onRefresh: () => void
  refreshing?: boolean
}

export function SimulationListToolbar({
  filters,
  onChange,
  versionOptions,
  organizationOptions,
  onRefresh,
  refreshing,
}: SimulationListToolbarProps) {
  const [advancedOpen, setAdvancedOpen] = useState(false)
  const advancedCount =
    (filters.organizationId !== 'all' ? 1 : 0) +
    (filters.datePreset !== 'all' ? 1 : 0)

  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
      <div className="flex min-w-0 flex-1 flex-wrap items-center gap-2">
        <Input
          className="h-9 min-w-[12rem] flex-1 sm:max-w-xs"
          placeholder="Search simulations…"
          value={filters.search}
          onChange={(event) => onChange({ search: event.target.value })}
        />
        <Select
          value={filters.status}
          onValueChange={(value) => onChange({ status: value })}
        >
          <SelectTrigger className="h-9 w-[9rem]">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            {STATUS_OPTIONS.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select
          value={filters.gameVersionId}
          onValueChange={(value) => onChange({ gameVersionId: value })}
        >
          <SelectTrigger className="h-9 w-[9rem]">
            <SelectValue placeholder="Version" />
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
        <Select
          value={filters.datePreset}
          onValueChange={(value) => onChange({ datePreset: value })}
        >
          <SelectTrigger className="h-9 w-[9rem]">
            <SelectValue placeholder="Date" />
          </SelectTrigger>
          <SelectContent>
            {DATE_OPTIONS.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Dialog open={advancedOpen} onOpenChange={setAdvancedOpen}>
          <DialogTrigger asChild>
            <Button variant="outline" size="sm" className="h-9 gap-2">
              <Filter className="h-4 w-4" />
              Advanced
              {advancedCount > 0 ? (
                <span className="rounded-full bg-primary/10 px-1.5 text-xs text-primary">
                  {advancedCount}
                </span>
              ) : null}
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Advanced filters</DialogTitle>
              <DialogDescription>
                Narrow results by organization or custom date range.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Organization</Label>
                <Select
                  value={filters.organizationId}
                  onValueChange={(value) => onChange({ organizationId: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All organizations</SelectItem>
                    {organizationOptions.map((org) => (
                      <SelectItem key={org.id} value={org.id}>
                        {org.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              {filters.datePreset === 'custom' && (
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="adv-date-from">From</Label>
                    <Input
                      id="adv-date-from"
                      type="date"
                      value={filters.dateFrom}
                      onChange={(event) =>
                        onChange({ dateFrom: event.target.value })
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="adv-date-to">To</Label>
                    <Input
                      id="adv-date-to"
                      type="date"
                      value={filters.dateTo}
                      onChange={(event) => onChange({ dateTo: event.target.value })}
                    />
                  </div>
                </div>
              )}
            </div>
            <DialogFooter>
              <Button
                variant="ghost"
                onClick={() => {
                  onChange({
                    organizationId: 'all',
                    datePreset: 'all',
                    dateFrom: '',
                    dateTo: '',
                  })
                }}
              >
                Clear
              </Button>
              <Button onClick={() => setAdvancedOpen(false)}>Apply</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
      <div className="flex shrink-0 items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          className="h-9"
          onClick={onRefresh}
          disabled={refreshing}
        >
          <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
          <span className="sr-only sm:not-sr-only sm:ml-2">Refresh</span>
        </Button>
        <Button asChild size="sm" className="h-9">
          <Link to="/simulations/create">
            <Plus className="h-4 w-4" />
            New simulation
          </Link>
        </Button>
      </div>
    </div>
  )
}

export function resolveDateRange(
  preset: string,
  dateFrom: string,
  dateTo: string,
): { from: string; to: string } {
  if (preset === 'custom') {
    return { from: dateFrom, to: dateTo }
  }
  if (preset === 'all') {
    return { from: '', to: '' }
  }
  const days = preset === '7d' ? 7 : preset === '30d' ? 30 : 90
  const to = new Date()
  const from = new Date()
  from.setDate(from.getDate() - days)
  return {
    from: from.toISOString().slice(0, 10),
    to: to.toISOString().slice(0, 10),
  }
}
