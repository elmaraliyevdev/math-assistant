export const MIN_ZOOM = 0.25
export const MAX_ZOOM = 1.5

export function clampZoom(value: number) {
  return Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, value))
}
