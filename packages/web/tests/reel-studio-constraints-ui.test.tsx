import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'

import simpleTemplate from '@/features/game-templates/templates/simple-5x3.json'
import { ConstraintEditor } from '@/features/reel-studio/constraints/components/ConstraintEditor'
import { ValidationSidebar } from '@/features/reel-studio/constraints/components/ValidationSidebar'
import { ConstraintStudioProvider } from '@/features/reel-studio/constraints/context/constraint-studio-context'
import { ReelStudioProvider } from '@/features/reel-studio/context/reel-studio-context'
import { parseCanonicalJson } from '@/features/reel-studio/lib/parse-canonical'

function renderDesignStudio(ui: React.ReactNode) {
  const document = parseCanonicalJson(
    simpleTemplate as Record<string, unknown>,
    'runtime-core@1.8.0',
  )
  return render(
    <ReelStudioProvider initialDocument={document}>
      <ConstraintStudioProvider>{ui}</ConstraintStudioProvider>
    </ReelStudioProvider>,
  )
}

describe('Constraint UI', () => {
  it('renders validation sidebar with summary', () => {
    renderDesignStudio(<ValidationSidebar />)
    expect(screen.getByText(/validation/i)).toBeInTheDocument()
  })

  it('adds constraints from editor', async () => {
    const user = userEvent.setup()
    renderDesignStudio(<ConstraintEditor />)
    await user.click(screen.getByRole('button', { name: /^add$/i }))
    expect(screen.getByDisplayValue('New constraint')).toBeInTheDocument()
  })
})
