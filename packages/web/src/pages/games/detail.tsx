import { useNavigate, useParams } from '@tanstack/react-router'
import { useState } from 'react'

import { ConfirmDialog } from '@/components/ui/confirm-dialog'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Skeleton } from '@/components/ui/skeleton'
import {
  JsonViewer,
  VersionTable,
  VersionUploadDialog,
} from '@/features/games/components'
import {
  useDeleteGame,
  useGame,
  useGameVersion,
  useGameVersions,
} from '@/features/games/hooks/use-games'
import type { GameVersionSummary } from '@/types/api'
import { formatDate } from '@/lib/utils'

function JsonPreviewDialog({
  gameId,
  version,
  onClose,
}: {
  gameId: string
  version: GameVersionSummary
  onClose: () => void
}) {
  const detail = useGameVersion(gameId, version.id)

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>Version {version.version} canonical JSON</DialogTitle>
        </DialogHeader>
        {detail.isLoading && <Skeleton className="h-48 w-full" />}
        {detail.data && <JsonViewer value={detail.data.canonicalJson} />}
      </DialogContent>
    </Dialog>
  )
}

export function GameDetailPage() {
  const { gameId } = useParams({ strict: false }) as { gameId: string }
  const navigate = useNavigate()
  const game = useGame(gameId)
  const versions = useGameVersions(gameId)
  const deleteGame = useDeleteGame()
  const [uploadOpen, setUploadOpen] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)
  const [jsonPreview, setJsonPreview] = useState<GameVersionSummary | null>(null)

  if (game.isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-48 w-full" />
      </div>
    )
  }

  if (!game.data) {
    return <p className="text-muted-foreground">Game not found.</p>
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">{game.data.name}</h2>
          <p className="text-muted-foreground">
            {game.data.description ?? 'No description'}
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setUploadOpen(true)}>Upload Version</Button>
          <Button variant="destructive" onClick={() => setDeleteOpen(true)}>
            Delete game
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Game information</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 text-sm sm:grid-cols-2">
          <div>
            <p className="text-muted-foreground">Created</p>
            <p className="font-medium">{formatDate(game.data.createdAt)}</p>
          </div>
          <div>
            <p className="text-muted-foreground">Updated</p>
            <p className="font-medium">{formatDate(game.data.updatedAt)}</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between gap-4 space-y-0">
          <CardTitle>Version history</CardTitle>
          <Button variant="outline" size="sm" onClick={() => setUploadOpen(true)}>
            Upload JSON
          </Button>
        </CardHeader>
        <CardContent>
          <VersionTable
            gameId={gameId}
            versions={versions.data ?? []}
            loading={versions.isLoading}
            onViewJson={setJsonPreview}
            onUploadJson={() => setUploadOpen(true)}
            onUseTemplate={() => navigate({ to: '/templates' })}
          />
        </CardContent>
      </Card>

      <VersionUploadDialog
        gameId={gameId}
        open={uploadOpen}
        onOpenChange={setUploadOpen}
      />

      <ConfirmDialog
        open={deleteOpen}
        onOpenChange={setDeleteOpen}
        title="Delete game"
        description={`Delete "${game.data.name}" and all versions?`}
        confirmLabel="Delete"
        destructive
        loading={deleteGame.isPending}
        onConfirm={() => deleteGame.mutate(gameId)}
      />

      {jsonPreview && (
        <JsonPreviewDialog
          gameId={gameId}
          version={jsonPreview}
          onClose={() => setJsonPreview(null)}
        />
      )}
    </div>
  )
}
