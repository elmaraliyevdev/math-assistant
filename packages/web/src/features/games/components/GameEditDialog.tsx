import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { GameForm } from '@/features/games/components/GameForm'
import { useUpdateGame } from '@/features/games/hooks/use-games'
import type { Game } from '@/types/api'

interface GameEditDialogProps {
  game: Game | null
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function GameEditDialog({ game, open, onOpenChange }: GameEditDialogProps) {
  const updateGame = useUpdateGame(game?.id ?? '')

  if (!game) {
    return null
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit game</DialogTitle>
        </DialogHeader>
        <GameForm
          defaultValues={{
            name: game.name,
            description: game.description ?? '',
          }}
          submitLabel="Save changes"
          loading={updateGame.isPending}
          onCancel={() => onOpenChange(false)}
          onSubmit={(values) => {
            updateGame.mutate(values, {
              onSuccess: () => onOpenChange(false),
            })
          }}
        />
      </DialogContent>
    </Dialog>
  )
}
