export type HeroSymbolType = 'regular' | 'wild' | 'scatter' | 'bonus'

export const HERO_SYMBOL_META: Record<
  string,
  { displayName: string; type: HeroSymbolType }
> = {
  HV1: { displayName: 'Crown', type: 'regular' },
  HV2: { displayName: 'Shield', type: 'regular' },
  LV1: { displayName: 'Ace', type: 'regular' },
  LV2: { displayName: 'King', type: 'regular' },
  WILD: { displayName: 'Wild', type: 'wild' },
  SCAT: { displayName: 'Scatter', type: 'scatter' },
  BONUS: { displayName: 'Hold & Win', type: 'bonus' },
}

export const HERO_REELS: string[][] = [
  ['HV1', 'LV1', 'WILD', 'LV2', 'HV2', 'LV1', 'SCAT'],
  ['SCAT', 'HV1', 'LV2', 'HV2', 'LV1', 'WILD', 'LV2'],
  ['HV2', 'WILD', 'LV1', 'LV2', 'HV1', 'BONUS', 'LV1'],
  ['LV2', 'HV1', 'SCAT', 'LV1', 'HV2', 'LV2', 'WILD'],
  ['LV1', 'HV2', 'LV2', 'WILD', 'LV1', 'HV1', 'LV2'],
]

export const HERO_PALETTE = ['HV1', 'HV2', 'LV1', 'LV2', 'WILD'] as const

export const HERO_SYMBOL_CODE: Record<string, string> = {
  HV1: 'HV1',
  HV2: 'HV2',
  LV1: 'LV1',
  LV2: 'LV2',
  WILD: 'WILD',
  SCAT: 'SCAT',
  BONUS: 'BONUS',
}

export const HERO_SYMBOL_CLASS: Record<HeroSymbolType, string> = {
  regular: 'bg-slate-700/90 text-slate-100',
  wild: 'bg-amber-900/90 text-amber-100',
  scatter: 'bg-violet-900/90 text-violet-100',
  bonus: 'bg-emerald-900/90 text-emerald-100',
}
