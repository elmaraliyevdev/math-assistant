import { renderHook } from '@testing-library/react'
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import {
  downloadTemplate,
  GAME_TEMPLATES,
  getTemplateById,
  TemplateDownloadCard,
  TemplatePreview,
  TemplateSelector,
} from '@/features/game-templates'
import { useGameTemplate, useGameTemplates } from '@/features/game-templates/hooks/use-game-templates'
import { VersionTable } from '@/features/games/components/VersionTable'
import { VersionUploadDialog } from '@/features/games/components/VersionUploadDialog'
import { gameKeys } from '@/features/games/hooks/use-games'
import { downloadBlob } from '@/lib/export'

import { server } from './msw'
import './msw'
import { expectHeading, renderAt, renderWithQuery } from './test-utils'

vi.mock('@/lib/export', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/lib/export')>()
  return {
    ...actual,
    downloadBlob: vi.fn(actual.downloadBlob),
  }
})

describe('game templates catalog', () => {
  it('exposes four canonical templates', () => {
    expect(GAME_TEMPLATES).toHaveLength(4)
    expect(getTemplateById('simple-5x3')?.name).toMatch(/simple 5/i)
    expect(getTemplateById('nested-features')?.features.length).toBeGreaterThan(0)
  })

  it('downloads template JSON', () => {
    const template = GAME_TEMPLATES[0]!
    downloadTemplate(template)
    expect(downloadBlob).toHaveBeenCalledWith(
      expect.any(Blob),
      template.filename,
    )
  })
})

describe('TemplateSelector', () => {
  it('selects a template', async () => {
    const user = userEvent.setup()
    const onSelect = vi.fn()
    render(
      <TemplateSelector
        templates={GAME_TEMPLATES}
        onSelect={onSelect}
      />,
    )

    await user.click(screen.getByRole('button', { name: /free spins slot/i }))
    expect(onSelect).toHaveBeenCalledWith(
      expect.objectContaining({ id: 'free-spins' }),
    )
  })
})

describe('TemplatePreview', () => {
  it('renders collapsible JSON viewer', () => {
    const template = GAME_TEMPLATES[0]!
    render(<TemplatePreview template={template} />)
    expect(screen.getByText(/canonical json/i)).toBeInTheDocument()
  })
})

describe('TemplateDownloadCard', () => {
  it('opens preview dialog', async () => {
    const user = userEvent.setup()
    const template = GAME_TEMPLATES[0]!

    render(
      <TemplateDownloadCard template={template} onUseTemplate={() => undefined} />,
    )

    await user.click(screen.getByRole('button', { name: /preview/i }))
    const dialog = await screen.findByRole('dialog')
    expect(within(dialog).getByText(/canonical json/i)).toBeInTheDocument()
  })
})

describe('templates page', () => {
  it('renders all template cards', async () => {
    await renderAt('/templates')
    await expectHeading(/templates/i)
    expect(await screen.findByText(/simple 5×3 slot/i)).toBeInTheDocument()
    expect(screen.getByText(/free spins slot/i)).toBeInTheDocument()
    expect(screen.getByText(/hold and win slot/i)).toBeInTheDocument()
    expect(screen.getByText(/nested features slot/i)).toBeInTheDocument()
  })

  it('downloads template from page', async () => {
    const user = userEvent.setup()
    await renderAt('/templates')
    const downloadButtons = await screen.findAllByRole('button', {
      name: /^download$/i,
    })
    await user.click(downloadButtons[0]!)
    expect(downloadBlob).toHaveBeenCalled()
  })

  it('uploads template to selected game', async () => {
    const user = userEvent.setup()
    let posted = false

    server.use(
      http.post('/api/games/:gameId/versions', async () => {
        posted = true
        return HttpResponse.json({
          id: 'version-new',
          version: 3,
          contentHash: 'hash-new',
          engineVersion: 'runtime-core@1.8.0',
          validationSummary: { passed: true, findingCount: 0, findings: [] },
        })
      }),
    )

    const { history } = await renderAt('/templates')
    await user.click(screen.getAllByRole('button', { name: /^use$/i })[0]!)

    const dialog = await screen.findByRole('dialog')
    expect(dialog).toBeInTheDocument()

    await user.click(screen.getByRole('combobox'))
    await user.click(await screen.findByText('Lucky Stars'))
    await user.click(screen.getByRole('button', { name: /upload template/i }))

    await waitFor(() => expect(posted).toBe(true))
    await waitFor(() =>
      expect(history.location.pathname).toBe('/games/game-1'),
    )
  })
})

describe('game detail upload UX', () => {
  it('shows Upload Version button in header', async () => {
    await renderAt('/games/game-1')
    expect(
      await screen.findByRole('button', { name: /^upload version$/i }),
    ).toBeInTheDocument()
  })

  it('opens upload dialog from header button', async () => {
    const user = userEvent.setup()
    await renderAt('/games/game-1')
    await user.click(await screen.findByRole('button', { name: /^upload version$/i }))
    expect(await screen.findByText(/upload game version/i)).toBeInTheDocument()
  })
})

describe('VersionTable empty state', () => {
  it('renders upload and template actions', async () => {
    const user = userEvent.setup()
    const onUpload = vi.fn()
    const onTemplate = vi.fn()

    render(
      <VersionTable
        gameId="game-1"
        versions={[]}
        onViewJson={() => undefined}
        onUploadJson={onUpload}
        onUseTemplate={onTemplate}
      />,
    )

    expect(screen.getByText(/no versions uploaded/i)).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: /upload json/i }))
    await user.click(screen.getByRole('button', { name: /use template/i }))
    expect(onUpload).toHaveBeenCalled()
    expect(onTemplate).toHaveBeenCalled()
  })

  it('shows empty state on game with no versions', async () => {
    server.use(
      http.get('/api/games/:gameId/versions', async () => HttpResponse.json([])),
    )

    await renderAt('/games/game-1')
    expect(await screen.findByText(/no versions uploaded/i)).toBeInTheDocument()
    expect(screen.getAllByRole('button', { name: /upload json/i }).length).toBeGreaterThan(0)
    expect(screen.getByRole('button', { name: /use template/i })).toBeInTheDocument()
  })
})

describe('VersionUploadDialog', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders upload tabs', () => {
    renderWithQuery(
      <VersionUploadDialog gameId="game-1" open onOpenChange={() => undefined} />,
    )
    expect(screen.getByRole('button', { name: /upload file/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /paste json/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /templates/i })).toBeInTheDocument()
  })

  it('validates invalid JSON on paste tab', async () => {
    const user = userEvent.setup()
    renderWithQuery(
      <VersionUploadDialog gameId="game-1" open onOpenChange={() => undefined} />,
    )

    await user.click(screen.getByRole('button', { name: /paste json/i }))
    const textarea = screen.getByLabelText(/canonical json/i)
    fireEvent.change(textarea, { target: { value: '{not-json' } })
    await user.click(screen.getByRole('button', { name: /create version/i }))

    expect(await screen.findByText(/invalid json syntax/i)).toBeInTheDocument()
  })

  it('loads template JSON from templates tab', async () => {
    const user = userEvent.setup()
    renderWithQuery(
      <VersionUploadDialog gameId="game-1" open onOpenChange={() => undefined} />,
    )

    await user.click(screen.getByRole('button', { name: /^templates$/i }))
    await user.click(screen.getByRole('button', { name: /hold and win slot/i }))
    expect(screen.getByText(/characters loaded/i)).toBeInTheDocument()
  })

  it('accepts valid JSON file on upload tab', async () => {
    const user = userEvent.setup()
    renderWithQuery(
      <VersionUploadDialog gameId="game-1" open onOpenChange={() => undefined} />,
    )

    const input = document.querySelector('input[type="file"]') as HTMLInputElement
    const file = new File(['{"schemaVersion":"1.0.0"}'], 'game.json', {
      type: 'application/json',
    })
    await user.upload(input, file)

    expect(await screen.findByText('game.json')).toBeInTheDocument()
  })

  it('shows error for invalid JSON file', async () => {
    const user = userEvent.setup()
    renderWithQuery(
      <VersionUploadDialog gameId="game-1" open onOpenChange={() => undefined} />,
    )

    const input = document.querySelector('input[type="file"]') as HTMLInputElement
    const file = new File(['not-json'], 'broken.json', { type: 'application/json' })
    await user.upload(input, file)

    expect(await screen.findByText(/does not contain valid json/i)).toBeInTheDocument()
  })

  it('resets state when dialog closes', async () => {
    const user = userEvent.setup()
    const onOpenChange = vi.fn()

    renderWithQuery(
      <VersionUploadDialog gameId="game-1" open onOpenChange={onOpenChange} />,
    )

    await user.click(screen.getByRole('button', { name: /cancel/i }))
    expect(onOpenChange).toHaveBeenCalledWith(false)
  })

  it('creates version and invalidates queries', async () => {
    const user = userEvent.setup()
    const { useAuthStore } = await import('@/stores/auth-store')
    useAuthStore.getState().setAccessToken('access-token')

    server.use(
      http.post('/api/games/:gameId/versions', async () =>
        HttpResponse.json({
          id: 'version-2',
          version: 2,
          contentHash: 'def456',
          engineVersion: 'runtime-core@1.8.0',
          validationSummary: { passed: true, findingCount: 0, findings: [] },
        }),
      ),
    )

    const { QueryClient, QueryClientProvider } = await import('@tanstack/react-query')
    const client = new QueryClient({
      defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
    })
    const invalidate = vi.spyOn(client, 'invalidateQueries')

    render(
      <QueryClientProvider client={client}>
        <VersionUploadDialog gameId="game-1" open onOpenChange={() => undefined} />
      </QueryClientProvider>,
    )

    await user.click(screen.getByRole('button', { name: /paste json/i }))
    fireEvent.change(screen.getByLabelText(/canonical json/i), {
      target: { value: '{"schemaVersion":"1.0.0"}' },
    })
    await user.click(screen.getByRole('button', { name: /create version/i }))

    await waitFor(() =>
      expect(invalidate).toHaveBeenCalledWith({
        queryKey: gameKeys.versions('game-1'),
      }),
    )
  })
})

describe('useGameTemplates hooks', () => {
  it('returns template catalog', () => {
    const { result } = renderHook(() => useGameTemplates())
    expect(result.current).toHaveLength(4)
  })

  it('looks up template by id', () => {
    const { result } = renderHook(() => useGameTemplate('hold-win'))
    expect(result.current?.id).toBe('hold-win')
  })

  it('returns undefined for unknown template id', () => {
    const { result } = renderHook(() => useGameTemplate('missing'))
    expect(result.current).toBeUndefined()
  })
})

describe('UseTemplateDialog via templates page', () => {
  it('requires game selection before upload', async () => {
    const user = userEvent.setup()
    await renderAt('/templates')
    await user.click(screen.getAllByRole('button', { name: /^use$/i })[0]!)

    expect(screen.getByRole('button', { name: /upload template/i })).toBeDisabled()
    await user.click(screen.getByRole('combobox'))
    await user.click(await screen.findByText('Lucky Stars'))
    expect(screen.getByRole('button', { name: /upload template/i })).toBeEnabled()
  })
})
