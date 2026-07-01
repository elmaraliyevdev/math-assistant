import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react'

import { clampZoom } from '@/features/reel-studio/layout/studio-zoom'
import type { ViewportTransform } from '@/features/reel-studio/workspace/viewport-math'

export type SelectedSlot = { reelIndex: number; symbolIndex: number }

type ViewportControls = {
  zoomIn: () => void
  zoomOut: () => void
  fit: () => void
  reset: () => void
}

type StudioCanvasContextValue = {
  transform: ViewportTransform
  setTransform: (
    transform: ViewportTransform | ((current: ViewportTransform) => ViewportTransform),
  ) => void
  zoom: number
  setZoom: (zoom: number) => void
  zoomIn: () => void
  zoomOut: () => void
  fitZoom: () => void
  resetZoom: () => void
  setFitZoomHandler: (handler: (() => void) | null) => void
  setViewportControls: (controls: ViewportControls | null) => void
  isSpacePressed: boolean
  setIsSpacePressed: (value: boolean) => void
  showGrid: boolean
  setShowGrid: (value: boolean) => void
  snapEnabled: boolean
  setSnapEnabled: (value: boolean) => void
  isFullscreen: boolean
  toggleFullscreen: () => void
  isPanning: boolean
  setIsPanning: (value: boolean) => void
  selectedReelIndex: number | null
  setSelectedReelIndex: (index: number | null) => void
  selectedSlot: SelectedSlot | null
  setSelectedSlot: (slot: SelectedSlot | null) => void
  activeDropTargetId: string | null
  setActiveDropTargetId: (id: string | null) => void
}

const StudioCanvasContext = createContext<StudioCanvasContextValue | null>(null)

const DEFAULT_TRANSFORM: ViewportTransform = { x: 0, y: 0, zoom: 1 }

export function StudioCanvasProvider({ children }: { children: ReactNode }) {
  const [transform, setTransformState] = useState<ViewportTransform>(DEFAULT_TRANSFORM)
  const [showGrid, setShowGrid] = useState(true)
  const [snapEnabled, setSnapEnabled] = useState(true)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [isPanning, setIsPanning] = useState(false)
  const [isSpacePressed, setIsSpacePressed] = useState(false)
  const [selectedReelIndex, setSelectedReelIndex] = useState<number | null>(null)
  const [selectedSlot, setSelectedSlot] = useState<SelectedSlot | null>(null)
  const [activeDropTargetId, setActiveDropTargetId] = useState<string | null>(null)
  const fitZoomHandlerRef = useRef<(() => void) | null>(null)
  const viewportControlsRef = useRef<ViewportControls | null>(null)

  const setTransform = useCallback(
    (next: ViewportTransform | ((current: ViewportTransform) => ViewportTransform)) => {
      setTransformState((current) => {
        const resolved = typeof next === 'function' ? next(current) : next
        return {
          x: resolved.x,
          y: resolved.y,
          zoom: clampZoom(resolved.zoom),
        }
      })
    },
    [],
  )

  const setZoom = useCallback(
    (zoom: number) => {
      setTransformState((current) => ({
        ...current,
        zoom: clampZoom(zoom),
      }))
    },
    [],
  )

  const setFitZoomHandler = useCallback((handler: (() => void) | null) => {
    fitZoomHandlerRef.current = handler
  }, [])

  const setViewportControls = useCallback((controls: ViewportControls | null) => {
    viewportControlsRef.current = controls
  }, [])

  const fitZoom = useCallback(() => {
    viewportControlsRef.current?.fit() ?? fitZoomHandlerRef.current?.()
  }, [])

  const resetZoom = useCallback(() => {
    viewportControlsRef.current?.reset() ?? setTransformState(DEFAULT_TRANSFORM)
  }, [])

  const zoomIn = useCallback(() => {
    viewportControlsRef.current?.zoomIn()
  }, [])

  const zoomOut = useCallback(() => {
    viewportControlsRef.current?.zoomOut()
  }, [])

  const toggleFullscreen = useCallback(() => {
    const root = document.querySelector('[data-studio-root]') as HTMLElement | null
    if (!document.fullscreenElement && root) {
      void root.requestFullscreen().then(() => setIsFullscreen(true))
      return
    }
    if (document.fullscreenElement) {
      void document.exitFullscreen().then(() => setIsFullscreen(false))
    }
  }, [])

  const value = useMemo(
    () => ({
      transform,
      setTransform,
      zoom: transform.zoom,
      setZoom,
      zoomIn,
      zoomOut,
      fitZoom,
      resetZoom,
      setFitZoomHandler,
      setViewportControls,
      isSpacePressed,
      setIsSpacePressed,
      showGrid,
      setShowGrid,
      snapEnabled,
      setSnapEnabled,
      isFullscreen,
      toggleFullscreen,
      isPanning,
      setIsPanning,
      selectedReelIndex,
      setSelectedReelIndex,
      selectedSlot,
      setSelectedSlot,
      activeDropTargetId,
      setActiveDropTargetId,
    }),
    [
      transform,
      setTransform,
      setZoom,
      zoomIn,
      zoomOut,
      fitZoom,
      resetZoom,
      setFitZoomHandler,
      setViewportControls,
      isSpacePressed,
      showGrid,
      snapEnabled,
      isFullscreen,
      toggleFullscreen,
      isPanning,
      selectedReelIndex,
      selectedSlot,
      activeDropTargetId,
    ],
  )

  return (
    <StudioCanvasContext.Provider value={value}>{children}</StudioCanvasContext.Provider>
  )
}

export function useStudioCanvas() {
  const context = useContext(StudioCanvasContext)
  if (!context) {
    throw new Error('useStudioCanvas must be used within StudioCanvasProvider')
  }
  return context
}
