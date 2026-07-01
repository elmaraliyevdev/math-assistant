'use client'

import { PreviewCertificationProvider } from '../../preview/PreviewCertificationProvider'
import { CertificationPreview } from '../../previews/CertificationPreview'
import { DemoSpotlight } from '../../shell/DemoSpotlight'

export type CertificationDemoProps = {
  previewMode?: boolean
}

export function CertificationDemo({ previewMode = true }: CertificationDemoProps) {
  return (
    <PreviewCertificationProvider previewMode={previewMode}>
      <DemoSpotlight previewMode={previewMode}>
        <CertificationPreview />
      </DemoSpotlight>
    </PreviewCertificationProvider>
  )
}
