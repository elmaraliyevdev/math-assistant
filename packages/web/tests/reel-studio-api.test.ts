import { describe, expect, it, vi } from 'vitest'

import { reelStudioApi } from '@/features/reel-studio/api/reel-studio-api'
import { api } from '@/services/api'

vi.mock('@/services/api', () => ({
  api: {
    post: vi.fn(),
  },
}))

describe('reelStudioApi', () => {
  it('calls merge endpoint', async () => {
    vi.mocked(api.post).mockResolvedValue({
      data: { canonicalJson: { schemaVersion: '1.0.0' } },
    })
    const result = await reelStudioApi.merge({
      canonicalJson: { schemaVersion: '1.0.0' },
      reelSets: {},
    })
    expect(api.post).toHaveBeenCalledWith('/reel-studio/merge', expect.any(Object))
    expect(result.canonicalJson.schemaVersion).toBe('1.0.0')
  })

  it('validates canonical JSON', async () => {
    vi.mocked(api.post).mockResolvedValue({
      data: { report: { passed: true, findings: [] } },
    })
    const result = await reelStudioApi.validate({ schemaVersion: '1.0.0' }, 'runtime-core@1.8.0')
    expect(api.post).toHaveBeenCalledWith('/games/validate', {
      canonicalJson: { schemaVersion: '1.0.0' },
      engineVersion: 'runtime-core@1.8.0',
    })
    expect(result.report?.passed).toBe(true)
  })

  it('builds preview locally', () => {
    const preview = reelStudioApi.buildPreview(
      { schemaVersion: '1.0.0', reelSets: { base_game: { id: 'base_game', reels: [] } } },
      {
        base_game: {
          id: 'base_game',
          reels: [{ reelIndex: 0, symbols: ['A'] }],
        },
      },
    )
    const reelSets = preview.reelSets as Record<string, { reels: Array<{ symbols: string[] }> }>
    expect(reelSets.base_game.reels[0]?.symbols).toEqual(['A'])
  })
})
