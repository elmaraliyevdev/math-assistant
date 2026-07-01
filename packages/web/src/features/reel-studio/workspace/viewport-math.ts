import { clampZoom } from '@/features/reel-studio/layout/studio-zoom'

export type ViewportTransform = {
  x: number
  y: number
  zoom: number
}

export function zoomAtPoint(
  transform: ViewportTransform,
  nextZoom: number,
  /** Cursor position relative to viewport container */
  pointX: number,
  pointY: number,
): ViewportTransform {
  const zoom = clampZoom(nextZoom)
  const worldX = (pointX - transform.x) / transform.zoom
  const worldY = (pointY - transform.y) / transform.zoom

  return {
    zoom,
    x: pointX - worldX * zoom,
    y: pointY - worldY * zoom,
  }
}

export function fitTransform(
  containerWidth: number,
  containerHeight: number,
  contentWidth: number,
  contentHeight: number,
  padding = 48,
): ViewportTransform {
  if (contentWidth <= 0 || contentHeight <= 0 || containerWidth <= 0 || containerHeight <= 0) {
    return { x: 0, y: 0, zoom: 1 }
  }

  const availableWidth = containerWidth - padding * 2
  const availableHeight = containerHeight - padding * 2
  const zoom = clampZoom(Math.min(availableWidth / contentWidth, availableHeight / contentHeight, 1))
  const scaledWidth = contentWidth * zoom
  const scaledHeight = contentHeight * zoom

  return {
    zoom,
    x: (containerWidth - scaledWidth) / 2,
    y: (containerHeight - scaledHeight) / 2,
  }
}

export function screenToWorld(
  transform: ViewportTransform,
  screenX: number,
  screenY: number,
): { x: number; y: number } {
  return {
    x: (screenX - transform.x) / transform.zoom,
    y: (screenY - transform.y) / transform.zoom,
  }
}
