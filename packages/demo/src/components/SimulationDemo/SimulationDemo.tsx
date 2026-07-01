'use client'

import { PreviewSimulationProvider } from '../../preview/PreviewSimulationProvider'
import { SimulationPreview } from '../../previews/SimulationPreview'
import { DemoSpotlight } from '../../shell/DemoSpotlight'

export type SimulationDemoProps = {
  previewMode?: boolean
}

export function SimulationDemo({ previewMode = true }: SimulationDemoProps) {
  return (
    <PreviewSimulationProvider previewMode={previewMode}>
      <DemoSpotlight previewMode={previewMode}>
        <SimulationPreview />
      </DemoSpotlight>
    </PreviewSimulationProvider>
  )
}
