import { useEffect } from 'react'

export function useStudioKeyboard({
  onSave,
  onUndo,
  onRedo,
  onOpenGame,
  onOpenAi,
  canUndo,
  canRedo,
}: {
  onSave: () => void
  onUndo: () => void
  onRedo: () => void
  onOpenGame: () => void
  onOpenAi: () => void
  canUndo: boolean
  canRedo: boolean
}) {
  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      const mod = event.metaKey || event.ctrlKey
      if (!mod) return

      const key = event.key.toLowerCase()
      if (key === 's') {
        event.preventDefault()
        onSave()
      } else if (key === 'z' && event.shiftKey && canRedo) {
        event.preventDefault()
        onRedo()
      } else if (key === 'z' && !event.shiftKey && canUndo) {
        event.preventDefault()
        onUndo()
      } else if (key === 'p') {
        event.preventDefault()
        onOpenGame()
      } else if (key === '/') {
        event.preventDefault()
        onOpenAi()
      }
    }

    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onSave, onUndo, onRedo, onOpenGame, onOpenAi, canUndo, canRedo])
}
