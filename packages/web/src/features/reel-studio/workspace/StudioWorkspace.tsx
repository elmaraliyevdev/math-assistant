import {
  useCallback,
  useEffect,
  useRef,
  type ReactNode,
  type WheelEvent as ReactWheelEvent,
} from 'react'

import { useStudioCanvas } from '@/features/reel-studio/layout/studio-canvas-context'
import { clampZoom } from '@/features/reel-studio/layout/studio-zoom'
import { studioPanState } from '@/features/reel-studio/workspace/studio-pan-state'
import { fitTransform, zoomAtPoint } from '@/features/reel-studio/workspace/viewport-math'
import { cn } from '@/lib/utils'

const CONTENT_PADDING = 48
const ZOOM_STEP = 1.12

type PanState = {
  pointerId: number
  startX: number
  startY: number
  originX: number
  originY: number
}

export function StudioWorkspace({
  children,
  className,
}: {
  children: ReactNode
  className?: string
}) {
  const {
    transform,
    setTransform,
    setFitZoomHandler,
    setViewportControls,
    showGrid,
    isPanning,
    setIsPanning,
    isSpacePressed,
    setIsSpacePressed,
  } = useStudioCanvas()

  const containerRef = useRef<HTMLDivElement>(null)
  const contentRef = useRef<HTMLDivElement>(null)
  const panRef = useRef<PanState | null>(null)
  const spacePressedRef = useRef(false)
  const hasFittedRef = useRef(false)

  const fitToContent = useCallback(() => {
    const container = containerRef.current
    const content = contentRef.current
    if (!container || !content) return

    const next = fitTransform(
      container.clientWidth,
      container.clientHeight,
      content.scrollWidth,
      content.scrollHeight,
      CONTENT_PADDING,
    )
    setTransform(next)
  }, [setTransform])

  const resetViewport = useCallback(() => {
    setTransform({ x: 0, y: 0, zoom: 1 })
  }, [setTransform])

  const zoomRelative = useCallback(
    (factor: number) => {
      const container = containerRef.current
      if (!container) return

      const pointX = container.clientWidth / 2
      const pointY = container.clientHeight / 2
      setTransform((current) =>
        zoomAtPoint(current, current.zoom * factor, pointX, pointY),
      )
    },
    [setTransform],
  )

  const zoomIn = useCallback(() => zoomRelative(ZOOM_STEP), [zoomRelative])
  const zoomOut = useCallback(() => zoomRelative(1 / ZOOM_STEP), [zoomRelative])

  useEffect(() => {
    setFitZoomHandler(fitToContent)
    return () => setFitZoomHandler(null)
  }, [fitToContent, setFitZoomHandler])

  useEffect(() => {
    setViewportControls({ zoomIn, zoomOut, fit: fitToContent, reset: resetViewport })
    return () => setViewportControls(null)
  }, [fitToContent, resetViewport, setViewportControls, zoomIn, zoomOut])

  useEffect(() => {
    studioPanState.spacePressed = isSpacePressed
    studioPanState.panning = isPanning
    spacePressedRef.current = isSpacePressed
  }, [isPanning, isSpacePressed])

  useEffect(() => {
    const content = contentRef.current
    if (!content || hasFittedRef.current) return

    const observer = new ResizeObserver(() => {
      if (content.scrollWidth > 0 && content.scrollHeight > 0 && !hasFittedRef.current) {
        hasFittedRef.current = true
        fitToContent()
      }
    })
    observer.observe(content)
    return () => observer.disconnect()
  }, [fitToContent])

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.code === 'Space' && !event.repeat) {
        const target = event.target as HTMLElement
        if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
          return
        }
        event.preventDefault()
        spacePressedRef.current = true
        setIsSpacePressed(true)
      }
    }
    const onKeyUp = (event: KeyboardEvent) => {
      if (event.code === 'Space') {
        spacePressedRef.current = false
        setIsSpacePressed(false)
        panRef.current = null
        setIsPanning(false)
      }
    }
    window.addEventListener('keydown', onKeyDown)
    window.addEventListener('keyup', onKeyUp)
    return () => {
      window.removeEventListener('keydown', onKeyDown)
      window.removeEventListener('keyup', onKeyUp)
    }
  }, [setIsPanning, setIsSpacePressed])

  const onWheel = useCallback(
    (event: ReactWheelEvent<HTMLDivElement>) => {
      event.preventDefault()
      const rect = containerRef.current?.getBoundingClientRect()
      if (!rect) return

      const pointX = event.clientX - rect.left
      const pointY = event.clientY - rect.top

      if (event.ctrlKey || event.metaKey) {
        const delta = -event.deltaY * 0.001
        setTransform((current) => {
          const nextZoom = clampZoom(current.zoom * (1 + delta))
          return zoomAtPoint(current, nextZoom, pointX, pointY)
        })
        return
      }

      setTransform((current) => ({
        ...current,
        x: current.x - event.deltaX,
        y: current.y - event.deltaY,
      }))
    },
    [setTransform],
  )

  const onPointerDown = useCallback(
    (event: React.PointerEvent<HTMLDivElement>) => {
      const isMiddleButton = event.button === 1
      const isSpacePan = spacePressedRef.current && event.button === 0

      if (!isMiddleButton && !isSpacePan) return

      event.preventDefault()
      event.currentTarget.setPointerCapture(event.pointerId)
      panRef.current = {
        pointerId: event.pointerId,
        startX: event.clientX,
        startY: event.clientY,
        originX: transform.x,
        originY: transform.y,
      }
      setIsPanning(true)
    },
    [setIsPanning, transform.x, transform.y],
  )

  const onPointerMove = useCallback(
    (event: React.PointerEvent<HTMLDivElement>) => {
      const pan = panRef.current
      if (!pan || pan.pointerId !== event.pointerId) return

      setTransform((current) => ({
        ...current,
        x: pan.originX + (event.clientX - pan.startX),
        y: pan.originY + (event.clientY - pan.startY),
      }))
    },
    [setTransform],
  )

  const onPointerUp = useCallback(
    (event: React.PointerEvent<HTMLDivElement>) => {
      const pan = panRef.current
      if (!pan || pan.pointerId !== event.pointerId) return

      panRef.current = null
      setIsPanning(false)
      if (event.currentTarget.hasPointerCapture(event.pointerId)) {
        event.currentTarget.releasePointerCapture(event.pointerId)
      }
    },
    [setIsPanning],
  )

  return (
    <div
      ref={containerRef}
      className={cn(
        'studio-workspace-viewport relative h-full w-full touch-none select-none overflow-hidden',
        isPanning || isSpacePressed ? 'cursor-grabbing' : 'cursor-default',
        isSpacePressed && !isPanning && 'cursor-grab',
        className,
      )}
      onWheel={onWheel}
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
      onPointerCancel={onPointerUp}
      onContextMenu={(event) => event.preventDefault()}
    >
      <div
        className={cn(
          'pointer-events-none absolute inset-0 studio-canvas',
          !showGrid && 'studio-canvas--no-grid',
        )}
      />
      <div
        className="absolute left-0 top-0 will-change-transform"
        style={{
          transform: `translate(${transform.x}px, ${transform.y}px) scale(${transform.zoom})`,
          transformOrigin: '0 0',
        }}
      >
        <div
          ref={contentRef}
          className="pointer-events-auto inline-block"
          style={{ padding: CONTENT_PADDING }}
        >
          {children}
        </div>
      </div>
    </div>
  )
}
