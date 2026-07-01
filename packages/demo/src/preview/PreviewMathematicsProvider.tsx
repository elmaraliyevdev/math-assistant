import type { ReactNode } from 'react'

import { PreviewModeProvider } from '@/features/preview/preview-mode-context'

export function PreviewMathematicsProvider({
  children,
  previewMode = true,
}: {
  children: ReactNode
  previewMode?: boolean
}) {
  return (
    <PreviewModeProvider previewMode={previewMode} readOnly demoMode>
      {children}
    </PreviewModeProvider>
  )
}
