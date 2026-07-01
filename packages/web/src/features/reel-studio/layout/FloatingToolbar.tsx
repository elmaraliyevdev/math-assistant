import { useNavigate } from '@tanstack/react-router'
import {
  Braces,
  FlaskConical,
  Redo2,
  Save,
  Sparkles,
  Undo2,
  Zap,
} from 'lucide-react'
import { useState } from 'react'

import { StudioIcon } from '@/components/studio/StudioIcon'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { useConstraintStudio } from '@/features/reel-studio/constraints/context/constraint-studio-context'
import { useReelStudio } from '@/features/reel-studio/context/reel-studio-context'
import { useGeneratorStudio } from '@/features/reel-studio/generator/context/generator-context'
import { useReelStudioSave } from '@/features/reel-studio/hooks/use-reel-studio-save'
import { useOptimizerStudio } from '@/features/reel-studio/optimizer/context/optimizer-context'
import { JsonViewer } from '@/features/games/components'
import { useReelStudioPreview } from '@/features/reel-studio/context/reel-studio-context'
import { cn } from '@/lib/utils'

const ICON_BTN = 'h-10 w-10 shrink-0'
const ACTION_BTN = 'h-10 gap-2 px-3 text-sm'

function JsonPreviewButton() {
  const previewJson = useReelStudioPreview()
  const [open, setOpen] = useState(false)

  return (
    <>
      <Button
        type="button"
        variant="ghost"
        className={ACTION_BTN}
        onClick={() => setOpen((value) => !value)}
        title="JSON preview"
      >
        <StudioIcon icon={Braces} />
        <span className="hidden sm:inline">JSON</span>
      </Button>
      {open ? (
        <div className="fixed inset-y-0 right-0 z-50 w-full max-w-xl border-l border-border bg-background/95 p-4 shadow-2xl backdrop-blur-md">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-lg font-medium">Canonical JSON</h3>
            <Button type="button" variant="ghost" onClick={() => setOpen(false)}>
              Close
            </Button>
          </div>
          <div className="h-[calc(100vh-6rem)] overflow-auto">
            <JsonViewer value={previewJson} />
          </div>
        </div>
      ) : null}
    </>
  )
}

export function FloatingToolbar({
  gameId,
  versionId,
}: {
  gameId: string
  versionId: string
}) {
  const navigate = useNavigate()
  const { document } = useReelStudio()
  const { canUndo, canRedo, undo, redo } = useConstraintStudio()
  const { generate, isGenerating } = useGeneratorStudio()
  const { optimizeTop, isOptimizing } = useOptimizerStudio()
  const save = useReelStudioSave(gameId)

  return (
    <div className="pointer-events-none absolute inset-x-0 top-4 z-20 flex justify-center px-4">
      <div
        className={cn(
          'pointer-events-auto flex items-center gap-1 rounded-xl p-1.5',
          'border border-border/40 bg-background/90 shadow-lg backdrop-blur-md',
          'transition-shadow duration-200 hover:shadow-xl',
        )}
      >
        <Button
          type="button"
          variant="ghost"
          className={ICON_BTN}
          disabled={!canUndo}
          onClick={undo}
          title="Undo"
        >
          <StudioIcon icon={Undo2} />
        </Button>
        <Button
          type="button"
          variant="ghost"
          className={ICON_BTN}
          disabled={!canRedo}
          onClick={redo}
          title="Redo"
        >
          <StudioIcon icon={Redo2} />
        </Button>

        <Separator orientation="vertical" className="mx-0.5 h-6" />

        <Button
          type="button"
          variant="ghost"
          className={ACTION_BTN}
          disabled={isGenerating}
          onClick={generate}
          title="Generate"
        >
          <StudioIcon icon={Sparkles} />
          <span className="hidden sm:inline">Generate</span>
        </Button>
        <Button
          type="button"
          variant="ghost"
          className={ACTION_BTN}
          disabled={isOptimizing}
          onClick={() => optimizeTop(5)}
          title="Optimize"
        >
          <StudioIcon icon={Zap} />
          <span className="hidden sm:inline">Optimize</span>
        </Button>
        <Button
          type="button"
          variant="ghost"
          className={ACTION_BTN}
          onClick={() =>
            navigate({
              to: '/simulations/create',
              search: { gameVersionId: versionId },
            })
          }
          title="Simulate"
        >
          <StudioIcon icon={FlaskConical} />
          <span className="hidden sm:inline">Simulate</span>
        </Button>

        <Separator orientation="vertical" className="mx-0.5 h-6" />

        <JsonPreviewButton />
        <Button
          type="button"
          className={ACTION_BTN}
          disabled={save.isPending}
          onClick={() => save.mutate(document)}
          title="Save"
        >
          <StudioIcon icon={Save} />
          <span className="hidden sm:inline">{save.isPending ? 'Saving…' : 'Save'}</span>
        </Button>
      </div>
    </div>
  )
}
