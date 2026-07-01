import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { SETTINGS_SECTIONS } from '@/features/settings/settings-sections'
import { renderAt } from './test-utils'

describe('settings sections', () => {
  for (const { id, label } of SETTINGS_SECTIONS) {
    it(`renders ${label} without crashing`, async () => {
      await renderAt(`/settings?section=${id}`)
      expect(await screen.findByRole('heading', { name: label, level: 2 })).toBeInTheDocument()
    })
  }
})
