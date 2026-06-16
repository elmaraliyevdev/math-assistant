import { create } from 'zustand'

type Theme = 'light' | 'dark'

function applyTheme(theme: Theme) {
  const root = document.documentElement
  root.classList.toggle('dark', theme === 'dark')
}

function readStoredTheme(): Theme {
  const stored = localStorage.getItem('ma_theme')
  if (stored === 'dark' || stored === 'light') {
    return stored
  }
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

interface ThemeState {
  theme: Theme
  initialize: () => void
  toggle: () => void
  setTheme: (theme: Theme) => void
}

export const useThemeStore = create<ThemeState>((set, get) => ({
  theme: 'light',
  initialize: () => {
    const theme = readStoredTheme()
    applyTheme(theme)
    set({ theme })
  },
  toggle: () => {
    const next = get().theme === 'dark' ? 'light' : 'dark'
    localStorage.setItem('ma_theme', next)
    applyTheme(next)
    set({ theme: next })
  },
  setTheme: (theme) => {
    localStorage.setItem('ma_theme', theme)
    applyTheme(theme)
    set({ theme })
  },
}))
