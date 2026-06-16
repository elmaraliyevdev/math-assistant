import { describe, expect, it, vi } from 'vitest'

import { downloadBlob, exportJson } from '@/lib/export'
import { captureApiError, initSentry } from '@/lib/sentry'

describe('export helpers', () => {
  it('downloads blob via temporary anchor', () => {
    const createObjectURL = vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:1')
    const revoke = vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {})
    const click = vi.fn()
    vi.spyOn(document, 'createElement').mockReturnValue({
      click,
      href: '',
      download: '',
    } as unknown as HTMLAnchorElement)

    downloadBlob(new Blob(['hello']), 'test.txt')
    expect(createObjectURL).toHaveBeenCalled()
    expect(click).toHaveBeenCalled()
    expect(revoke).toHaveBeenCalled()

    createObjectURL.mockRestore()
    revoke.mockRestore()
  })

  it('exports json data', () => {
    const createObjectURL = vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:1')
    const revoke = vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {})
    const click = vi.fn()
    vi.spyOn(document, 'createElement').mockReturnValue({
      click,
      href: '',
      download: '',
    } as unknown as HTMLAnchorElement)

    exportJson('data.json', { ok: true })
    expect(click).toHaveBeenCalled()

    createObjectURL.mockRestore()
    revoke.mockRestore()
  })
})

describe('sentry helpers', () => {
  it('skips init without dsn', () => {
    expect(() => initSentry()).not.toThrow()
  })

  it('skips capture without dsn', () => {
    expect(() => captureApiError(new Error('boom'))).not.toThrow()
  })
})
