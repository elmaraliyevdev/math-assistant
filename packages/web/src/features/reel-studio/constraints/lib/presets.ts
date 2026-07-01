import type { ConstraintDocument, ConstraintPreset } from '@/features/reel-studio/constraints/types'

const BASE_GROUPS = {
  premium: { id: 'premium', name: 'Premium', symbolIds: [] as string[] },
  low: { id: 'low', name: 'Low', symbolIds: [] as string[] },
  wild: { id: 'wild', name: 'Wild', symbolIds: [] as string[] },
  scatter: { id: 'scatter', name: 'Scatter', symbolIds: [] as string[] },
  bonus: { id: 'bonus', name: 'Bonus', symbolIds: [] as string[] },
}

function rule(
  partial: Omit<ConstraintDocument['constraints'][number], 'enabled' | 'scope' | 'severity'> &
    Partial<Pick<ConstraintDocument['constraints'][number], 'scope' | 'severity'>>,
): ConstraintDocument['constraints'][number] {
  return {
    enabled: true,
    scope: 'global',
    severity: 'error',
    ...partial,
  }
}

function buildPreset(
  id: string,
  name: string,
  description: string,
  constraints: ConstraintDocument['constraints'],
  edgeWrapping = true,
): ConstraintPreset {
  return {
    id,
    name,
    description,
    builtIn: true,
    document: {
      version: 1,
      edgeWrapping,
      groups: Object.values(BASE_GROUPS).map((group) => ({ ...group })),
      inventory: {},
      constraints,
    },
  }
}

export const BUILTIN_PRESETS: ConstraintPreset[] = [
  buildPreset(
    'generic',
    'Generic',
    'Balanced scatter spacing and wild separation.',
    [
      rule({
        id: 'generic-scatter-min',
        type: 'min_count',
        description: 'Scatter minimum across reels',
        targetType: 'group',
        targetId: 'scatter',
        value: 3,
      }),
      rule({
        id: 'generic-scatter-distance',
        type: 'min_distance',
        description: 'Scatter minimum distance',
        targetType: 'group',
        targetId: 'scatter',
        value: 3,
      }),
      rule({
        id: 'generic-wild-adjacency',
        type: 'forbidden_adjacency',
        description: 'Wild cannot touch wild',
        targetType: 'group',
        targetId: 'wild',
        value: 0,
      }),
    ],
  ),
  buildPreset(
    'high_volatility',
    'High Volatility',
    'Fewer premiums, tighter scatter spacing, limited wild stacks.',
    [
      rule({
        id: 'hv-scatter-max-consecutive',
        type: 'max_consecutive',
        description: 'Scatter max consecutive',
        targetType: 'group',
        targetId: 'scatter',
        value: 1,
      }),
      rule({
        id: 'hv-wild-max',
        type: 'max_count',
        description: 'Wild maximum total',
        targetType: 'group',
        targetId: 'wild',
        value: 6,
      }),
      rule({
        id: 'hv-premium-min-distance',
        type: 'min_distance',
        description: 'Premium minimum distance',
        targetType: 'group',
        targetId: 'premium',
        value: 2,
      }),
    ],
  ),
  buildPreset(
    'medium_volatility',
    'Medium Volatility',
    'Moderate scatter distance and wild caps.',
    [
      rule({
        id: 'mv-scatter-distance',
        type: 'min_distance',
        description: 'Scatter minimum distance',
        targetType: 'group',
        targetId: 'scatter',
        value: 2,
      }),
      rule({
        id: 'mv-wild-max-consecutive',
        type: 'max_consecutive',
        description: 'Wild max consecutive',
        targetType: 'group',
        targetId: 'wild',
        value: 2,
      }),
    ],
  ),
  buildPreset(
    'low_volatility',
    'Low Volatility',
    'Higher low-symbol density, generous spacing for features.',
    [
      rule({
        id: 'lv-low-min',
        type: 'min_count',
        description: 'Low symbols minimum',
        targetType: 'group',
        targetId: 'low',
        value: 20,
      }),
      rule({
        id: 'lv-scatter-distance',
        type: 'min_distance',
        description: 'Scatter minimum distance',
        targetType: 'group',
        targetId: 'scatter',
        value: 4,
      }),
    ],
  ),
  buildPreset(
    'hold_and_win',
    'Hold & Win',
    'Bonus symbol spacing and edge-aware adjacency.',
    [
      rule({
        id: 'hnw-bonus-forbidden',
        type: 'forbidden_adjacency',
        description: 'Bonus cannot touch bonus',
        targetType: 'group',
        targetId: 'bonus',
        value: 0,
      }),
      rule({
        id: 'hnw-bonus-distance',
        type: 'min_distance',
        description: 'Bonus minimum distance',
        targetType: 'group',
        targetId: 'bonus',
        value: 2,
      }),
    ],
    true,
  ),
  buildPreset(
    'free_spins',
    'Free Spins',
    'Scatter placement rules for feature reels.',
    [
      rule({
        id: 'fs-scatter-min',
        type: 'min_count',
        description: 'Scatter minimum in feature set',
        targetType: 'group',
        targetId: 'scatter',
        value: 5,
      }),
      rule({
        id: 'fs-scatter-max-consecutive',
        type: 'max_consecutive',
        description: 'Scatter max consecutive',
        targetType: 'group',
        targetId: 'scatter',
        value: 1,
      }),
    ],
  ),
]

export function hydratePresetGroups(
  preset: ConstraintPreset,
  symbols: Record<string, { id: string; type: string }>,
): ConstraintDocument {
  const premium: string[] = []
  const low: string[] = []
  const wild: string[] = []
  const scatter: string[] = []
  const bonus: string[] = []
  for (const symbol of Object.values(symbols)) {
    if (symbol.type === 'wild') wild.push(symbol.id)
    else if (symbol.type === 'scatter') scatter.push(symbol.id)
    else if (symbol.type === 'bonus') bonus.push(symbol.id)
    else if (symbol.id.startsWith('H') || symbol.id.includes('HIGH')) premium.push(symbol.id)
    else low.push(symbol.id)
  }
  const groups = preset.document.groups.map((group) => {
    if (group.id === 'premium') return { ...group, symbolIds: premium }
    if (group.id === 'low') return { ...group, symbolIds: low }
    if (group.id === 'wild') return { ...group, symbolIds: wild }
    if (group.id === 'scatter') return { ...group, symbolIds: scatter }
    if (group.id === 'bonus') return { ...group, symbolIds: bonus }
    return group
  })
  return {
    ...preset.document,
    groups,
    activePresetId: preset.id,
  }
}

export function listPresets(custom: ConstraintPreset[] = []): ConstraintPreset[] {
  return [...BUILTIN_PRESETS, ...custom]
}
