import { describe, it } from 'vitest'

import { expectHeading, renderAt } from './test-utils'

describe('Reel Studio landing', () => {
  it('shows mathematical design studio onboarding', async () => {
    await renderAt('/reel-studio')
    await expectHeading(/mathematical design studio/i)
  })
})
