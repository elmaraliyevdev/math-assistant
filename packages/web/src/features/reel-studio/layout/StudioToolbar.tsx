import { useNavigate } from '@tanstack/react-router'
import {
  FlaskConical,
  Redo2,
  Save,
  Sparkles,
  Undo2,
  Zap,
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { ReelSetSelector } from '@/features/reel-studio/components/ReelSetSelector'
import { useConstraintStudio } from '@/features/reel-studio/constraints/context/constraint-studio-context'
import { useReelStudio } from '@/features/reel-studio/context/reel-studio-context'
import { useGeneratorStudio } from '@/features/reel-studio/generator/context/generator-context'
import { useReelStudioSave } from '@/features/reel-studio/hooks/use-reel-studio-save'
import { useOptimizerStudio } from '@/features/reel-studio/optimizer/context/optimizer-context'
import { JsonPreviewDrawer } from '@/features/reel-studio/components/JsonPreviewDrawer'

export function StudioToolbar({
  gameId,
  versionId,
  gameName,
  versionNumber,
}: {
  gameId: string
  versionId: string
  gameName: string
  versionNumber: number
}) {
  const navigate = useNavigate()
  const { document } = useReelStudio()
  const { canUndo, canRedo, undo, redo } = useConstraintStudio()
  const { generate, isGenerating } = useGeneratorStudio()
  const { optimizeTop, isOptimizing } = useOptimizerStudio()
  const save = useReelStudioSave(gameId)

  return (
    <header className="studio-toolbar flex flex-wrap items-center gap-2 border-b border-border/50 px-1 py-2">
      <div className="flex min-w-0 flex-1 items-center gap-3">
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold">{gameName}</p>
          <p className="text-xs text-muted-foreground">Version {versionNumber}</p>
        </div>
        <ReelSetSelector />
      </div>

      <div className="flex flex-wrap items-center gap-1">
        <Button type="button" size="sm" variant="ghost" disabled={!canUndo} onClick={undo}>
          <Undo2 className="h-4 w-4" />
        </Button>
        <Button type="button" size="sm" variant="ghost" disabled={!canRedo} onClick={redo}>
          <Redo2 className="h-4 w-4" />
        </Button>
        <div className="mx-1 h-5 w-px bg-border/60" />
        <Button
          type="button"
          size="sm"
          variant="secondary"
          className="bg-primary/10 text-primary hover:bg-primary/20"
          disabled={isGenerating}
          onClick={generate}
        >
          <Sparkles className="h-4 w-4" />
          Generate
        </Button>
        <Button
          type="button"
          size="sm"
          variant="secondary"
          className="bg-primary/10 text-primary hover:bg-primary/20"
          disabled={isOptimizing}
          onClick={() => optimizeTop(5)}
        >
          <Zap className="h-4 w-4" />
          Optimize
        </Button>
        <Button
          type="button"
          size="sm"
          variant="ghost"
          onClick={() =>
            navigate({
              to: '/simulations/create',
              search: { gameVersionId: versionId },
            })
          }
        >
          <FlaskConical className="h-4 w-4" />
          Simulate
        </Button>
        <div className="mx-1 h-5 w-px bg-border/60" />
        <JsonPreviewDrawer />
        <Button
          type="button"
          size="sm"
          disabled={save.isPending}
          onClick={() => save.mutate(document)}
        >
          <Save className="h-4 w-4" />
          {save.isPending ? 'Saving…' : 'Save version'}
        </Button>
      </div>
    </header>
  )
}
