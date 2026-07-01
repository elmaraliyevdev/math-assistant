import { Link } from '@tanstack/react-router'
import { FileJson, LayoutTemplate } from 'lucide-react'

import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { GAME_TEMPLATES } from '@/features/game-templates/api/templates-api'

const PRESETS = [
  { id: 'classic', label: 'Classic 5×3', templateId: 'simple-5x3' },
  { id: 'hold-win', label: 'Hold & Win', templateId: 'hold-win' },
  { id: 'free-spins', label: 'Free Spins', templateId: 'free-spins' },
  { id: 'megaways', label: 'Megaways', templateId: null },
  { id: 'blank', label: 'Blank', templateId: null },
] as const

export function CreatePresetDialog({
  open,
  onOpenChange,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Create new game</DialogTitle>
        </DialogHeader>
        <p className="text-sm text-muted-foreground">
          Start from a mathematical preset or build from scratch.
        </p>
        <div className="grid gap-2 pt-2">
          {PRESETS.map((preset) => {
            const template = preset.templateId
              ? GAME_TEMPLATES.find((entry) => entry.id === preset.templateId)
              : null
            return (
              <Button
                key={preset.id}
                variant="outline"
                className="h-auto justify-start px-3 py-2.5"
                asChild
              >
                <Link
                  to={template ? '/templates' : '/games/create'}
                  onClick={() => onOpenChange(false)}
                >
                  <div className="text-left">
                    <p className="font-medium">{preset.label}</p>
                    {template ? (
                      <p className="text-xs text-muted-foreground">{template.description}</p>
                    ) : (
                      <p className="text-xs text-muted-foreground">
                        {preset.id === 'megaways' ? 'Coming soon' : 'Empty canonical JSON'}
                      </p>
                    )}
                  </div>
                </Link>
              </Button>
            )
          })}
          <Button variant="secondary" className="gap-2" asChild>
            <Link to="/templates" onClick={() => onOpenChange(false)}>
              <LayoutTemplate className="h-4 w-4" />
              Browse all templates
            </Link>
          </Button>
          <Button variant="ghost" className="gap-2" asChild>
            <Link to="/games/create" onClick={() => onOpenChange(false)}>
              <FileJson className="h-4 w-4" />
              Import JSON
            </Link>
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
