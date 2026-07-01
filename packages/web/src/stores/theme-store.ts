import { create } from 'zustand'

export type ThemePreference = 'light' | 'dark' | 'system'
type ResolvedTheme = 'light' | 'dark'

function getSystemTheme(): ResolvedTheme {
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function resolveTheme(preference: ThemePreference): ResolvedTheme {
  return preference === 'system' ? getSystemTheme() : preference
}

function applyTheme(preference: ThemePreference) {
  const resolved = resolveTheme(preference)
  document.documentElement.classList.toggle('dark', resolved === 'dark')
}

function readStoredTheme(): ThemePreference {
  const stored = localStorage.getItem('ma_theme')
  if (stored === 'dark' || stored === 'light' || stored === 'system') {
    return stored
  }
  return 'system'
}

let systemListenerAttached = false

function attachSystemListener(setResolved: () => void) {
  if (systemListenerAttached) return
  systemListenerAttached = true
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    setResolved()
  })
}

if (typeof window !== 'undefined') {
  applyTheme(readStoredTheme())
}

interface ThemeState {
  theme: ThemePreference
  resolvedTheme: ResolvedTheme
  initialize: () => void
  toggle: () => void
  setTheme: (theme: ThemePreference) => void
}

export const useThemeStore = create<ThemeState>((set, get) => ({
  theme: typeof window !== 'undefined' ? readStoredTheme() : 'system',
  resolvedTheme:
    typeof window !== 'undefined' ? resolveTheme(readStoredTheme()) : 'light',
  initialize: () => {
    const theme = readStoredTheme()
    applyTheme(theme)
    set({ theme, resolvedTheme: resolveTheme(theme) })
    attachSystemListener(() => {
      const current = get().theme
      if (current === 'system') {
        applyTheme('system')
        set({ resolvedTheme: resolveTheme('system') })
      }
    })
  },
  toggle: () => {
    const resolved = resolveTheme(get().theme)
    const next: ThemePreference = resolved === 'dark' ? 'light' : 'dark'
    localStorage.setItem('ma_theme', next)
    applyTheme(next)
    set({ theme: next, resolvedTheme: resolveTheme(next) })
  },
  setTheme: (theme) => {
    localStorage.setItem('ma_theme', theme)
    applyTheme(theme)
    set({ theme, resolvedTheme: resolveTheme(theme) })
  },
}))
