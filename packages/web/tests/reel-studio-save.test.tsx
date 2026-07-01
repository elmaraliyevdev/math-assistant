import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, renderHook, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { gamesApi } from '@/features/games/api/games-api'
import { useReelStudioSave } from '@/features/reel-studio/hooks/use-reel-studio-save'
import { parseCanonicalJson } from '@/features/reel-studio/lib/parse-canonical'
import simpleTemplate from '@/features/game-templates/templates/simple-5x3.json'

const navigate = vi.fn()

vi.mock('@tanstack/react-router', () => ({
  useNavigate: () => navigate,
}))

vi.mock('@/features/games/api/games-api', () => ({
  gamesApi: {
    createVersion: vi.fn(),
  },
}))

vi.mock('@/lib/toast', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

describe('useReelStudioSave', () => {
  it('creates a new version with merged canonical JSON', async () => {
    vi.mocked(gamesApi.createVersion).mockResolvedValue({
      id: 'version-2',
      version: 2,
      validationSummary: { findingCount: 0 },
    } as Awaited<ReturnType<typeof gamesApi.createVersion>>)

    const document = parseCanonicalJson(
      simpleTemplate as Record<string, unknown>,
      'runtime-core@1.8.0',
    )
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    const { result } = renderHook(() => useReelStudioSave('game-1'), {
      wrapper: ({ children }) => (
        <QueryClientProvider client={client}>{children}</QueryClientProvider>
      ),
    })

    act(() => {
      result.current.mutate(document)
    })

    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(gamesApi.createVersion).toHaveBeenCalledWith(
      'game-1',
      expect.objectContaining({
        engineVersion: 'runtime-core@1.8.0',
        canonicalJson: expect.objectContaining({ schemaVersion: '1.0.0' }),
      }),
    )
    expect(navigate).toHaveBeenCalled()
  })

  it('reports generic save errors', async () => {
    vi.mocked(gamesApi.createVersion).mockRejectedValue(new Error('network'))
    const document = parseCanonicalJson(
      simpleTemplate as Record<string, unknown>,
      'runtime-core@1.8.0',
    )
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    const { result } = renderHook(() => useReelStudioSave('game-1'), {
      wrapper: ({ children }) => (
        <QueryClientProvider client={client}>{children}</QueryClientProvider>
      ),
    })

    act(() => {
      result.current.mutate(document)
    })

    await waitFor(() => expect(result.current.isError).toBe(true))
  })
})
