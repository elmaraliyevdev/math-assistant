import type { ReactNode } from 'react'

import { ConstraintStudioProvider } from '@/features/reel-studio/constraints/context/constraint-studio-context'
import { ReelStudioProvider } from '@/features/reel-studio/context/reel-studio-context'
import { GeneratorProvider } from '@/features/reel-studio/generator/context/generator-context'
import { StudioCanvasProvider } from '@/features/reel-studio/layout/studio-canvas-context'
import { OptimizerProvider } from '@/features/reel-studio/optimizer/context/optimizer-context'
import { PreviewModeProvider } from '@/features/preview/preview-mode-context'

import { demoReelStudioDocument } from '../data/reel-studio'

export function PreviewReelStudioProvider({
  children,
  previewMode = true,
}: {
  children: ReactNode
  previewMode?: boolean
}) {
  return (
    <PreviewModeProvider previewMode={previewMode} readOnly demoMode>
      <ReelStudioProvider initialDocument={demoReelStudioDocument}>
        <ConstraintStudioProvider>
          <GeneratorProvider>
            <OptimizerProvider>
              <StudioCanvasProvider>{children}</StudioCanvasProvider>
            </OptimizerProvider>
          </GeneratorProvider>
        </ConstraintStudioProvider>
      </ReelStudioProvider>
    </PreviewModeProvider>
  )
}
