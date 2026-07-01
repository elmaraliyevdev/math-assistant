'use client'

import { ConstraintsPreview } from '../../previews/ConstraintsPreview'
import { DemoSpotlight } from '../../shell/DemoSpotlight'

export type ReelStudioDemoProps = {
  previewMode?: boolean
}

/** Constraint validation marketing demo for the design walkthrough section. */
export function ReelStudioDemo({ previewMode = true }: ReelStudioDemoProps) {
  return (
    <DemoSpotlight previewMode={previewMode}>
      <ConstraintsPreview />
    </DemoSpotlight>
  )
}
