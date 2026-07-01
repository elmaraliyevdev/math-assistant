import { Link } from '@tanstack/react-router'
import { Dices, Plus, Search } from 'lucide-react'

import {
  EmptyState,
  PageHeader,
  PageToolbar,
  StatusBadge,
  toneForProjectStatus,
} from '@/components/design-system'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import type { GameListSort } from '@/features/games/hooks/use-games-with-status'
import type { GameListStatusFilter } from '@/features/games/lib/game-status'
import type { ProjectStatus } from '@/features/workspace/lib/workspace-status'
import { cn } from '@/lib/utils'

const FILTERS: Array<{ id: GameListStatusFilter; label: string }> = [
  { id: 'all', label: 'All' },
  { id: 'draft', label: 'Draft' },
  { id: 'ready', label: 'Ready' },
  { id: 'certified', label: 'Certified' },
  { id: 'simulating', label: 'Simulating' },
]

export function GamesToolbar({
  search,
  onSearchChange,
  filter,
  onFilterChange,
  sort,
  onSortChange,
}: {
  search: string
  onSearchChange: (value: string) => void
  filter: GameListStatusFilter
  onFilterChange: (value: GameListStatusFilter) => void
  sort: GameListSort
  onSortChange: (value: GameListSort) => void
}) {
  return (
    <>
      <PageHeader
        title="Games"
        description="Your slot projects"
        actions={
          <Button asChild>
            <Link to="/games/create">
              <Plus className="h-4 w-4" />
              New game
            </Link>
          </Button>
        }
      />

      <PageToolbar className="justify-between lg:items-center">
        <div className="relative min-w-0 flex-1 lg:max-w-md">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search games…"
            value={search}
            onChange={(event) => onSearchChange(event.target.value)}
            className="pl-9"
          />
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex flex-wrap gap-1 rounded-xl bg-muted p-1">
            {FILTERS.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => onFilterChange(item.id)}
                className={cn(
                  'rounded-lg px-3 py-1.5 text-xs font-medium transition-colors',
                  filter === item.id
                    ? 'bg-background text-foreground shadow-sm'
                    : 'text-muted-foreground hover:text-foreground',
                )}
              >
                {item.label}
              </button>
            ))}
          </div>
          <select
            value={sort}
            onChange={(event) => onSortChange(event.target.value as GameListSort)}
            className="h-9 rounded-lg border border-border bg-background px-3 text-sm"
            aria-label="Sort games"
          >
            <option value="updated">Sort: Last updated</option>
            <option value="name">Sort: Name</option>
          </select>
        </div>
      </PageToolbar>
    </>
  )
}

export function GamesEmptyState({ hasSearch }: { hasSearch: boolean }) {
  if (hasSearch) {
    return (
      <EmptyState
        icon={Dices}
        title="No games match your search"
        description="Try a different name or filter."
      />
    )
  }

  return (
    <EmptyState
      icon={Dices}
      title="No games yet"
      description="Create your first slot game to start designing reel strips and running simulations."
      action={
        <Button asChild>
          <Link to="/games/create">Create game</Link>
        </Button>
      }
    />
  )
}

export function GameStatusBadge({
  label,
  status,
}: {
  label: string
  status: ProjectStatus
}) {
  return <StatusBadge label={label} tone={toneForProjectStatus(status)} />
}
