const PINS_KEY = 'ma_studio_pinned_games'

export function getPinnedGameIds(): string[] {
  try {
    const raw = localStorage.getItem(PINS_KEY)
    return raw ? (JSON.parse(raw) as string[]) : []
  } catch {
    return []
  }
}

export function togglePinnedGame(gameId: string): string[] {
  const current = getPinnedGameIds()
  const next = current.includes(gameId)
    ? current.filter((id) => id !== gameId)
    : [gameId, ...current]
  localStorage.setItem(PINS_KEY, JSON.stringify(next.slice(0, 12)))
  return next
}

export function isGamePinned(gameId: string): boolean {
  return getPinnedGameIds().includes(gameId)
}
