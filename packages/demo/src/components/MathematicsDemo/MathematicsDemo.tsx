'use client'

import { PreviewMathematicsProvider } from '../../preview/PreviewMathematicsProvider'
import { MathematicsPreview } from '../../previews/MathematicsPreview'
import { DemoSpotlight } from '../../shell/DemoSpotlight'

export type MathematicsDemoProps = {
  previewMode?: boolean
}

export function MathematicsDemo({ previewMode = true }: MathematicsDemoProps) {
  return (
    <PreviewMathematicsProvider previewMode={previewMode}>
      <DemoSpotlight previewMode={previewMode}>
        <MathematicsPreview />
      </DemoSpotlight>
    </PreviewMathematicsProvider>
  )
}

export { demoCalibrateResponse } from '../../data/mathematics'
