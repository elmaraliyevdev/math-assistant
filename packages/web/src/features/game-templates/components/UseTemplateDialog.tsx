import { useState } from 'react'

import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { GameTemplate } from '@/features/game-templates/types'
import { DuplicateVersionNotice } from '@/features/games/components/DuplicateVersionNotice'
import {
  getDuplicateVersionDetails,
  useCreateGameVersion,
  useGames,
} from '@/features/games/hooks/use-games'
import { DEFAULT_ENGINE_VERSION } from '@/features/games/schemas/game-schemas'

interface UseTemplateDialogProps {
  template: GameTemplate | null
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function UseTemplateDialog({
  template,
  open,
  onOpenChange,
}: UseTemplateDialogProps) {
  const games = useGames({ page: 1, pageSize: 100 })
  const [gameId, setGameId] = useState('')
  const createVersion = useCreateGameVersion(gameId, { navigateTo: 'game' })
  const duplicateDetails = createVersion.isError
    ? getDuplicateVersionDetails(createVersion.error)
    : null

  function handleClose(nextOpen: boolean) {
    if (!nextOpen) {
      setGameId('')
      createVersion.reset()
    }
    onOpenChange(nextOpen)
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Use template</DialogTitle>
          <DialogDescription>
            Upload {template?.name ?? 'template'} to an existing game.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-2">
          <Label>Select game</Label>
          <Select value={gameId} onValueChange={setGameId}>
            <SelectTrigger>
              <SelectValue placeholder="Choose a game" />
            </SelectTrigger>
            <SelectContent>
              {games.data?.items.map((game) => (
                <SelectItem key={game.id} value={game.id}>
                  {game.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {duplicateDetails && (
          <DuplicateVersionNotice
            details={duplicateDetails}
            onCancel={() => handleClose(false)}
          />
        )}

        {!duplicateDetails && (
          <DialogFooter>
            <Button variant="outline" onClick={() => handleClose(false)}>
              Cancel
            </Button>
            <Button
              disabled={!gameId || !template || createVersion.isPending}
              onClick={() => {
                if (!template) return
                createVersion.mutate({
                  canonicalJson: template.canonicalJson,
                  engineVersion: DEFAULT_ENGINE_VERSION,
                })
              }}
            >
              {createVersion.isPending ? 'Uploading…' : 'Upload template'}
            </Button>
          </DialogFooter>
        )}
      </DialogContent>
    </Dialog>
  )
}
