export type WorkspaceMode =
  | 'design'
  | 'symbols'
  | 'constraints'
  | 'optimization'
  | 'ai'

export type BottomDrawerTab =
  | 'validation'
  | 'simulation'
  | 'statistics'
  | 'console'

const DOCK_HEIGHT_KEY = 'mathstudio-dock-height'

export function loadDockHeight(): number {
  try {
    const raw = localStorage.getItem(DOCK_HEIGHT_KEY)
    if (raw) {
      const parsed = Number(raw)
      if (parsed >= 120 && parsed <= 480) return parsed
    }
  } catch {
    /* ignore */
  }
  return 240
}

export function saveDockHeight(height: number) {
  try {
    localStorage.setItem(DOCK_HEIGHT_KEY, String(height))
  } catch {
    /* ignore */
  }
}
