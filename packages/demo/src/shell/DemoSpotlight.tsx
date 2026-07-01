import type { ReactNode } from 'react'

import { PreviewModeProvider } from '@/features/preview/preview-mode-context'

import { cn } from '../lib/cn'

import { DEMO_SPOTLIGHT_DESIGN_WIDTH, DemoScale } from './DemoScale'

import '../styles/demo-spotlight.css'

export type DemoSpotlightProps = {
  children: ReactNode
  className?: string
  previewMode?: boolean
}

/**
 * Unified marketing frame — identical radius, shadow, and padding across all demos.
 */
export function DemoSpotlight({
  children,
  className,
  previewMode = true,
}: DemoSpotlightProps) {
  return (
    <PreviewModeProvider previewMode={previewMode} readOnly demoMode>
      <DemoScale designWidth={DEMO_SPOTLIGHT_DESIGN_WIDTH}>
        <div
          className={cn(
            'demo-spotlight',
            previewMode && 'pointer-events-none select-none',
            className,
          )}
          aria-hidden={previewMode || undefined}
        >
          <div className="demo-spotlight-glow" aria-hidden />
          <div className="demo-spotlight-inner">
            <div className="demo-spotlight-crop">{children}</div>
          </div>
        </div>
      </DemoScale>
    </PreviewModeProvider>
  )
}
