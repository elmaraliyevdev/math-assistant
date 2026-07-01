const FAVORITES_KEY = 'ma_template_favorites'
const RECENT_KEY = 'ma_template_recent'

export function getFavoriteTemplateIds(): string[] {
  try {
    const raw = localStorage.getItem(FAVORITES_KEY)
    return raw ? (JSON.parse(raw) as string[]) : []
  } catch {
    return []
  }
}

export function toggleFavoriteTemplate(id: string): string[] {
  const current = getFavoriteTemplateIds()
  const next = current.includes(id)
    ? current.filter((entry) => entry !== id)
    : [...current, id]
  localStorage.setItem(FAVORITES_KEY, JSON.stringify(next))
  return next
}

export function getRecentTemplateIds(): string[] {
  try {
    const raw = localStorage.getItem(RECENT_KEY)
    return raw ? (JSON.parse(raw) as string[]) : []
  } catch {
    return []
  }
}

export function markTemplateUsed(id: string): string[] {
  const current = getRecentTemplateIds().filter((entry) => entry !== id)
  const next = [id, ...current].slice(0, 8)
  localStorage.setItem(RECENT_KEY, JSON.stringify(next))
  return next
}
