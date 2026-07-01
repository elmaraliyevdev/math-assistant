import { useNavigate } from '@tanstack/react-router'
import {
  Braces,
  FlaskConical,
  Focus,
  Grid3x3,
  Magnet,
  Maximize2,
  Minimize2,
  Minus,
  Plus,
  Redo2,
  RotateCcw,
  Save,
  Sparkles,
  Undo2,
  Zap,
} from 'lucide-react'
import { useState } from 'react'

import { StudioIcon } from '@/components/studio/StudioIcon'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { JsonViewer } from '@/features/games/components'
import { useConstraintStudio } from '@/features/reel-studio/constraints/context/constraint-studio-context'
import { useReelStudio, useReelStudioPreview } from '@/features/reel-studio/context/reel-studio-context'
import { useGeneratorStudio } from '@/features/reel-studio/generator/context/generator-context'
import { useReelStudioSave } from '@/features/reel-studio/hooks/use-reel-studio-save'
import { useStudioCanvas } from '@/features/reel-studio/layout/studio-canvas-context'
import { useOptimizerStudio } from '@/features/reel-studio/optimizer/context/optimizer-context'

function JsonPreviewButton() {
  const previewJson = useReelStudioPreview()
  const [open, setOpen] = useState(false)

  return (
    <>
      <Button
        type="button"
        variant="ghost"
        className="h-9 gap-2 px-3"
        onClick={() => setOpen((value) => !value)}
        title="JSON preview"
      >
        <StudioIcon icon={Braces} />
        <span className="hidden md:inline">JSON</span>
      </Button>
      {open ? (
        <div className="fixed inset-y-0 right-0 z-50 w-full max-w-xl border-l border-border/40 bg-background/95 p-4 shadow-2xl backdrop-blur-md">
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

export function StudioEditorToolbar({
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
  const {
    zoom,
    zoomIn,
    zoomOut,
    fitZoom,
    resetZoom,
    showGrid,
    setShowGrid,
    snapEnabled,
    setSnapEnabled,
    isFullscreen,
    toggleFullscreen,
  } = useStudioCanvas()

  return (
    <div className="studio-editor-toolbar flex h-10 shrink-0 items-center gap-1 border-b border-border/20 px-4 md:px-5">
      <div className="flex min-w-0 flex-1 items-center gap-1 overflow-x-auto">
        <Button type="button" variant="ghost" className="h-8 w-8 shrink-0" disabled={!canUndo} onClick={undo} title="Undo">
          <StudioIcon icon={Undo2} />
        </Button>
        <Button type="button" variant="ghost" className="h-8 w-8 shrink-0" disabled={!canRedo} onClick={redo} title="Redo">
          <StudioIcon icon={Redo2} />
        </Button>

        <Separator orientation="vertical" className="mx-1 h-5" />

        <Button type="button" variant="secondary" className="h-8 gap-2 px-3" disabled={isGenerating} onClick={generate}>
          <StudioIcon icon={Sparkles} />
          <span className="hidden sm:inline">Generate</span>
        </Button>
        <Button type="button" variant="secondary" className="h-8 gap-2 px-3" disabled={isOptimizing} onClick={() => optimizeTop(5)}>
          <StudioIcon icon={Zap} />
          <span className="hidden sm:inline">Optimize</span>
        </Button>

        <Separator orientation="vertical" className="mx-1 h-5" />

        <Button
          type="button"
          variant="ghost"
          className="h-8 gap-2 px-3"
          onClick={() => navigate({ to: '/simulations/create', search: { gameVersionId: versionId } })}
        >
          <StudioIcon icon={FlaskConical} />
          <span className="hidden sm:inline">Simulate</span>
        </Button>

        <Separator orientation="vertical" className="mx-1 h-5" />

        <JsonPreviewButton />
        <Button
          type="button"
          className="h-8 gap-2 px-3"
          disabled={save.isPending}
          onClick={() => save.mutate(document)}
        >
          <StudioIcon icon={Save} />
          <span className="hidden sm:inline">{save.isPending ? 'Saving…' : 'Save'}</span>
        </Button>
      </div>

      <div className="hidden shrink-0 items-center gap-0.5 sm:flex">
        <Separator orientation="vertical" className="mx-2 h-5" />
        <Button type="button" variant="ghost" className="h-8 w-8" onClick={zoomOut} title="Zoom out">
          <StudioIcon icon={Minus} />
        </Button>
        <span className="min-w-[3rem] text-center text-xs font-medium tabular-nums text-muted-foreground">
          {Math.round(zoom * 100)}%
        </span>
        <Button type="button" variant="ghost" className="h-8 w-8" onClick={zoomIn} title="Zoom in">
          <StudioIcon icon={Plus} />
        </Button>
        <Button type="button" variant="ghost" className="h-8 w-8" onClick={fitZoom} title="Fit screen">
          <StudioIcon icon={Focus} />
        </Button>
        <Button type="button" variant="ghost" className="h-8 w-8" onClick={resetZoom} title="Reset zoom">
          <StudioIcon icon={RotateCcw} />
        </Button>
        <Button type="button" variant={showGrid ? 'secondary' : 'ghost'} className="h-8 w-8" onClick={() => setShowGrid(!showGrid)} title="Grid">
          <StudioIcon icon={Grid3x3} />
        </Button>
        <Button type="button" variant={snapEnabled ? 'secondary' : 'ghost'} className="h-8 w-8" onClick={() => setSnapEnabled(!snapEnabled)} title="Snap">
          <StudioIcon icon={Magnet} />
        </Button>
        <Button type="button" variant="ghost" className="h-8 w-8" onClick={toggleFullscreen} title="Fullscreen">
          <StudioIcon icon={isFullscreen ? Minimize2 : Maximize2} />
        </Button>
      </div>
    </div>
  )
}
