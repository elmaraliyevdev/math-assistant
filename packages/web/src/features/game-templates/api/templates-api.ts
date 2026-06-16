import simple5x3 from '@/features/game-templates/templates/simple-5x3.json'
import freeSpins from '@/features/game-templates/templates/free-spins.json'
import holdWin from '@/features/game-templates/templates/hold-win.json'
import nestedFeatures from '@/features/game-templates/templates/nested-features.json'
import type { GameTemplate } from '@/features/game-templates/types'
import { downloadBlob } from '@/lib/export'

export const GAME_TEMPLATES: GameTemplate[] = [
  {
    id: 'simple-5x3',
    name: 'Simple 5×3 Slot',
    description: 'Classic base game with wilds and paylines — ideal first template.',
    features: ['Base Game', '5 reels', '3 rows', '10 paylines', 'Wild symbol', 'RTP 96%'],
    filename: 'simple-5x3.json',
    canonicalJson: simple5x3 as Record<string, unknown>,
  },
  {
    id: 'free-spins',
    name: 'Free Spins Slot',
    description: 'Scatter-triggered free spins with retrigger support.',
    features: ['Base Game', 'Free Spins', '3 scatter → 10 spins', 'Retrigger support'],
    filename: 'free-spins.json',
    canonicalJson: freeSpins as Record<string, unknown>,
  },
  {
    id: 'hold-win',
    name: 'Hold and Win Slot',
    description: 'Bonus symbols lock in place with respin mechanics.',
    features: ['Base Game', 'Hold & Win', 'Bonus symbols', 'Respins'],
    filename: 'hold-win.json',
    canonicalJson: holdWin as Record<string, unknown>,
  },
  {
    id: 'nested-features',
    name: 'Nested Features Slot',
    description: 'Free spins containing a nested hold & win feature.',
    features: ['Base Game', 'Free Spins', 'Hold & Win inside Free Spins'],
    filename: 'nested-features.json',
    canonicalJson: nestedFeatures as Record<string, unknown>,
  },
]

export function getTemplateById(id: string): GameTemplate | undefined {
  return GAME_TEMPLATES.find((template) => template.id === id)
}

export function downloadTemplate(template: GameTemplate) {
  const blob = new Blob([JSON.stringify(template.canonicalJson, null, 2)], {
    type: 'application/json',
  })
  downloadBlob(blob, template.filename)
}
