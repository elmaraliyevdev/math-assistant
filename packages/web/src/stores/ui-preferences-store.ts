import { create } from 'zustand'

export type UiDensity = 'compact' | 'comfortable'
export type UiAccent = 'blue' | 'violet' | 'emerald' | 'amber'
export type ChartTheme = 'default' | 'muted' | 'high-contrast'
export type CodeFont = 'jetbrains' | 'fira' | 'system'

interface UiPreferencesState {
  density: UiDensity
  accent: UiAccent
  animations: boolean
  sidebarCollapsed: boolean
  codeFont: CodeFont
  chartTheme: ChartTheme
  setDensity: (density: UiDensity) => void
  setAccent: (accent: UiAccent) => void
  setAnimations: (enabled: boolean) => void
  setSidebarCollapsed: (collapsed: boolean) => void
  setCodeFont: (font: CodeFont) => void
  setChartTheme: (theme: ChartTheme) => void
  initialize: () => void
}

function readBool(key: string, fallback: boolean) {
  const value = localStorage.getItem(key)
  if (value === 'true') return true
  if (value === 'false') return false
  return fallback
}

function readString<T extends string>(key: string, allowed: T[], fallback: T): T {
  const value = localStorage.getItem(key)
  return allowed.includes(value as T) ? (value as T) : fallback
}

export const useUiPreferencesStore = create<UiPreferencesState>((set) => ({
  density: 'comfortable',
  accent: 'blue',
  animations: true,
  sidebarCollapsed: false,
  codeFont: 'jetbrains',
  chartTheme: 'default',
  initialize: () => {
    set({
      density: readString<UiDensity>('ma_ui_density', ['compact', 'comfortable'], 'comfortable'),
      accent: readString<UiAccent>('ma_ui_accent', ['blue', 'violet', 'emerald', 'amber'], 'blue'),
      animations: readBool('ma_ui_animations', true),
      sidebarCollapsed: readBool('ma_ui_sidebar_collapsed', false),
      codeFont: readString<CodeFont>('ma_code_font', ['jetbrains', 'fira', 'system'], 'jetbrains'),
      chartTheme: readString<ChartTheme>(
        'ma_chart_theme',
        ['default', 'muted', 'high-contrast'],
        'default',
      ),
    })
  },
  setDensity: (density) => {
    localStorage.setItem('ma_ui_density', density)
    set({ density })
  },
  setAccent: (accent) => {
    localStorage.setItem('ma_ui_accent', accent)
    set({ accent })
  },
  setAnimations: (animations) => {
    localStorage.setItem('ma_ui_animations', String(animations))
    set({ animations })
  },
  setSidebarCollapsed: (sidebarCollapsed) => {
    localStorage.setItem('ma_ui_sidebar_collapsed', String(sidebarCollapsed))
    set({ sidebarCollapsed })
  },
  setCodeFont: (codeFont) => {
    localStorage.setItem('ma_code_font', codeFont)
    set({ codeFont })
  },
  setChartTheme: (chartTheme) => {
    localStorage.setItem('ma_chart_theme', chartTheme)
    set({ chartTheme })
  },
}))

if (typeof window !== 'undefined') {
  useUiPreferencesStore.getState().initialize()
}
