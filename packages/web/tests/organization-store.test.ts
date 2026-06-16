import { act } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { useOrganizationStore } from '@/stores/organization-store'

describe('organization store', () => {
  it('switches current organization', () => {
    act(() => {
      useOrganizationStore.getState().setCurrentOrganizationId('org-a')
    })
    expect(useOrganizationStore.getState().currentOrganizationId).toBe('org-a')

    act(() => {
      useOrganizationStore.getState().setCurrentOrganizationId('org-b')
    })
    expect(useOrganizationStore.getState().currentOrganizationId).toBe('org-b')
  })
})
