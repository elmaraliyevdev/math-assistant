import { Link } from '@tanstack/react-router'
import { Copy, Eye, Pencil, Trash2 } from 'lucide-react'
import { useState } from 'react'

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
import type { GameTableRow } from '@/features/games/types'
import { formatDate } from '@/lib/utils'
import { toast } from '@/lib/toast'

interface GameTableProps {
  rows: GameTableRow[]
  loading?: boolean
  onEdit: (game: GameTableRow) => void
  onDelete: (game: GameTableRow) => void
}

export function GameTable({ rows, loading, onEdit, onDelete }: GameTableProps) {
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
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Description</TableHead>
          <TableHead>Organization</TableHead>
          <TableHead>Created</TableHead>
          <TableHead>Versions</TableHead>
          <TableHead className="text-right">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map((game) => (
          <TableRow key={game.id}>
            <TableCell className="font-medium">
              <Link
                to="/games/$gameId"
                params={{ gameId: game.id }}
                className="hover:underline"
              >
                {game.name}
              </Link>
            </TableCell>
            <TableCell className="max-w-xs truncate text-muted-foreground">
              {game.description ?? '—'}
            </TableCell>
            <TableCell>{game.organizationName}</TableCell>
            <TableCell>{formatDate(game.createdAt)}</TableCell>
            <TableCell>{game.versionCount}</TableCell>
            <TableCell>
              <div className="flex justify-end gap-1">
                <Button variant="ghost" size="icon" asChild>
                  <Link to="/games/$gameId" params={{ gameId: game.id }}>
                    <Eye className="h-4 w-4" />
                    <span className="sr-only">View</span>
                  </Link>
                </Button>
                <Button variant="ghost" size="icon" onClick={() => onEdit(game)}>
                  <Pencil className="h-4 w-4" />
                  <span className="sr-only">Edit</span>
                </Button>
                <Button variant="ghost" size="icon" onClick={() => onDelete(game)}>
                  <Trash2 className="h-4 w-4 text-destructive" />
                  <span className="sr-only">Delete</span>
                </Button>
              </div>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}

export function GameTableEmpty({ hasSearch }: { hasSearch: boolean }) {
  return (
    <EmptyState
      title={hasSearch ? 'No games match your search' : 'No games yet'}
      description={
        hasSearch
          ? 'Try a different search term.'
          : 'Create your first game to upload mathematical models and run simulations.'
      }
      actions={
        !hasSearch ? (
          <>
            <Button asChild>
              <Link to="/games/create">Create game</Link>
            </Button>
            <Button variant="outline" asChild>
              <Link to="/templates">Browse templates</Link>
            </Button>
          </>
        ) : undefined
      }
    />
  )
}

export function CopyHashButton({ hash }: { hash: string }) {
  const [copied, setCopied] = useState(false)

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={async () => {
        await navigator.clipboard.writeText(hash)
        setCopied(true)
        toast.success('Content hash copied')
        window.setTimeout(() => setCopied(false), 1500)
      }}
    >
      <Copy className="h-4 w-4" />
      {copied ? 'Copied' : 'Copy hash'}
    </Button>
  )
}
