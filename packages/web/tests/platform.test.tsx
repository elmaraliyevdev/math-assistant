import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { MetricsOverview } from '@/features/dashboard/components/MetricsOverview'
import { SimulationExportMenu } from '@/features/exports/components/SimulationExportMenu'
import { NotificationCenter } from '@/features/notifications/components/NotificationCenter'
import { exportsApi } from '@/services/exports'
import { notificationsApi } from '@/services/notifications'
import { settingsApi } from '@/services/settings'
import { auditApi } from '@/services/audit'
import { dashboardApi } from '@/services/dashboard'
import { renderAt, renderWithQuery } from './test-utils'

describe('platform services', () => {
  it('loads notifications', async () => {
    const data = await notificationsApi.list()
    expect(data.items.length).toBeGreaterThan(0)
    expect(data.unreadCount).toBeGreaterThanOrEqual(1)
  })

  it('marks notifications read', async () => {
    const marked = await notificationsApi.markRead('notif-1')
    expect(marked.status).toBe(200)
  })

  it('marks all notifications read', async () => {
    const marked = await notificationsApi.markAllRead()
    expect(marked.status).toBe(200)
  })

  it('loads audit logs', async () => {
    const data = await auditApi.list()
    expect(data.items[0]?.action).toBe('auth.login')
  })

  it('loads and updates settings', async () => {
    const prefs = await settingsApi.getPreferences()
    expect(prefs.theme).toBe('light')
    const updated = await settingsApi.updatePreferences({ theme: 'dark' })
    expect(updated.theme).toBe('dark')
  })

  it('updates profile and changes password', async () => {
    const profile = await settingsApi.updateProfile({ fullName: 'New Name' })
    expect(profile.fullName).toBe('New Name')
    const password = await settingsApi.changePassword({
      currentPassword: 'secure-password',
      newPassword: 'another-secure-password',
    })
    expect(password.status).toBe(204)
  })

  it('loads dashboard summary', async () => {
    const summary = await dashboardApi.getSummary()
    expect(summary.totalSimulations).toBe(12)
    expect(summary.recentActivity.length).toBeGreaterThan(0)
  })
})

describe('notification center', () => {
  it('opens and shows notifications', async () => {
    const user = userEvent.setup()
    renderWithQuery(<NotificationCenter />)

    await user.click(screen.getByRole('button', { name: /notifications/i }))
    expect(await screen.findByText(/simulation completed/i)).toBeInTheDocument()
  })

  it('marks all notifications read', async () => {
    const user = userEvent.setup()
    renderWithQuery(<NotificationCenter />)
    await user.click(screen.getByRole('button', { name: /notifications/i }))
    await user.click(await screen.findByRole('button', { name: /mark all read/i }))
    await waitFor(() => {
      expect(screen.getByText(/simulation completed/i)).toBeInTheDocument()
    })
  })
})

describe('audit section', () => {
  it('renders audit entries and filters', async () => {
    const user = userEvent.setup()
    await renderAt('/settings?section=audit')

    expect(await screen.findByText(/test user/i)).toBeInTheDocument()
    await user.type(screen.getByPlaceholderText(/search activity/i), 'user-1')
  })
})

describe('settings page', () => {
  it('renders profile and notification preferences', async () => {
    const user = userEvent.setup()
    await renderAt('/settings')

    expect(await screen.findByLabelText(/full name/i)).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: /save profile/i }))
  })
})

describe('metrics overview', () => {
  it('renders prometheus metrics cards', async () => {
    renderWithQuery(<MetricsOverview />)
    expect(await screen.findByText(/system metrics/i)).toBeInTheDocument()
    expect(await screen.findByText(/api requests/i)).toBeInTheDocument()
  })
})

describe('exports api', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('downloads simulation export blob', async () => {
    const createObjectURL = vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:1')
    const revoke = vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {})
    const click = vi.fn()
    vi.spyOn(document, 'createElement').mockReturnValue({
      click,
      href: '',
      download: '',
    } as unknown as HTMLAnchorElement)

    await exportsApi.downloadSimulation('sim-1', 'json')
    expect(createObjectURL).toHaveBeenCalled()
    expect(click).toHaveBeenCalled()

    createObjectURL.mockRestore()
    revoke.mockRestore()
  })

  it('downloads game version export blob', async () => {
    const createObjectURL = vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:1')
    const revoke = vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {})
    const click = vi.fn()
    vi.spyOn(document, 'createElement').mockReturnValue({
      click,
      href: '',
      download: '',
    } as unknown as HTMLAnchorElement)

    await exportsApi.downloadGameVersion('game-1', 'version-1')
    expect(click).toHaveBeenCalled()

    createObjectURL.mockRestore()
    revoke.mockRestore()
  })
})

describe('simulation export menu', () => {
  it('exports selected format', async () => {
    const user = userEvent.setup()
    const download = vi
      .spyOn(exportsApi, 'downloadSimulation')
      .mockResolvedValue(undefined)

    renderWithQuery(<SimulationExportMenu simulationId="sim-completed" />)
    await user.click(screen.getByRole('button', { name: /export/i }))

    await waitFor(() => {
      expect(download).toHaveBeenCalledWith('sim-completed', 'json')
    })

    download.mockRestore()
  })
})
