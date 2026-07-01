import type { SymbolType } from '@/features/reel-studio/types'

const SYMBOL_TYPE_COLORS: Record<SymbolType, string> = {
  regular: 'bg-slate-200 text-slate-800 dark:bg-slate-700 dark:text-slate-100',
  wild: 'bg-amber-200 text-amber-950 dark:bg-amber-900 dark:text-amber-100',
  scatter: 'bg-primary/20 text-primary dark:bg-primary/30 dark:text-primary-foreground',
  bonus: 'bg-emerald-200 text-emerald-950 dark:bg-emerald-900 dark:text-emerald-100',
}

export function symbolTypeBadgeClass(type: SymbolType): string {
  return SYMBOL_TYPE_COLORS[type] ?? SYMBOL_TYPE_COLORS.regular
}

export function normalizeSymbolType(value: unknown): SymbolType {
  if (value === 'wild' || value === 'scatter' || value === 'bonus') {
    return value
  }
  return 'regular'
}
