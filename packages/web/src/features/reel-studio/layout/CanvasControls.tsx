import {
  Focus,
  Grid3x3,
  Magnet,
  Maximize2,
  Minimize2,
  Minus,
  Plus,
  RotateCcw,
} from 'lucide-react'

import { StudioIcon } from '@/components/studio/StudioIcon'
import { Button } from '@/components/ui/button'
import { useStudioCanvas } from '@/features/reel-studio/layout/studio-canvas-context'
import { cn } from '@/lib/utils'

const CONTROL_BTN = 'h-10 w-10 shrink-0'

function ControlCluster({
  children,
  className,
}: {
  children: React.ReactNode
  className?: string
}) {
  return (
    <div
      className={cn(
        'flex items-center gap-0.5 rounded-lg border border-border/40 bg-background/90 p-1 shadow-md backdrop-blur-md',
        className,
      )}
    >
      {children}
    </div>
  )
}

export function CanvasControls() {
  const {
    zoom,
    setZoom,
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
    <>
      <div className="pointer-events-none absolute left-4 top-16 z-10">
        <ControlCluster className="pointer-events-auto">
          <Button
            type="button"
            variant="ghost"
            className={CONTROL_BTN}
            onClick={() => setZoom(Math.max(0.5, zoom - 0.1))}
            title="Zoom out"
          >
            <StudioIcon icon={Minus} />
          </Button>
          <span className="min-w-[3rem] px-1 text-center text-sm font-medium tabular-nums text-foreground">
            {Math.round(zoom * 100)}%
          </span>
          <Button
            type="button"
            variant="ghost"
            className={CONTROL_BTN}
            onClick={() => setZoom(Math.min(1.5, zoom + 0.1))}
            title="Zoom in"
          >
            <StudioIcon icon={Plus} />
          </Button>
          <Button
            type="button"
            variant="ghost"
            className={CONTROL_BTN}
            onClick={fitZoom}
            title="Fit"
          >
            <StudioIcon icon={Focus} />
          </Button>
          <Button
            type="button"
            variant="ghost"
            className={CONTROL_BTN}
            onClick={resetZoom}
            title="Reset zoom"
          >
            <StudioIcon icon={RotateCcw} />
          </Button>
        </ControlCluster>
      </div>

      <div className="pointer-events-none absolute right-4 top-16 z-10">
        <ControlCluster className="pointer-events-auto">
          <Button
            type="button"
            variant={showGrid ? 'secondary' : 'ghost'}
            className={CONTROL_BTN}
            onClick={() => setShowGrid(!showGrid)}
            title="Toggle grid"
          >
            <StudioIcon icon={Grid3x3} />
          </Button>
          <Button
            type="button"
            variant={snapEnabled ? 'secondary' : 'ghost'}
            className={CONTROL_BTN}
            onClick={() => setSnapEnabled(!snapEnabled)}
            title="Snap"
          >
            <StudioIcon icon={Magnet} />
          </Button>
          <Button
            type="button"
            variant="ghost"
            className={CONTROL_BTN}
            onClick={toggleFullscreen}
            title="Fullscreen"
          >
            <StudioIcon icon={isFullscreen ? Minimize2 : Maximize2} />
          </Button>
        </ControlCluster>
      </div>
    </>
  )
}
