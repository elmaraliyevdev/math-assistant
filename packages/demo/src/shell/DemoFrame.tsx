import type { ReactNode } from 'react'

import {
  PreviewAppChrome,
  PreviewModeProvider,
  type PreviewNavId,
} from '@/features/preview/presentation'

import { DemoViewport } from './DemoViewport'
import { cn } from '../lib/cn'

import '../styles/demo-frame.css'

export type DemoFrameProps = {
  children: ReactNode
  activeNav?: PreviewNavId
  breadcrumb?: string
  title?: string
  toolbar?: ReactNode
  className?: string
  previewMode?: boolean
}

/**
 * @deprecated Use `DemoSpotlight` for marketing crops. Full app chrome is no longer used on the landing.
 */
export function DemoFrame({
  children,
  activeNav = 'reel-studio',
  breadcrumb,
  title,
  toolbar,
  className,
  previewMode = true,
}: DemoFrameProps) {
  return (
    <PreviewModeProvider previewMode={previewMode} readOnly demoMode>
      <div
        className={cn(
          'demo-frame overflow-hidden rounded-lg border border-border/80 bg-background shadow-2xl shadow-black/40',
          className,
        )}
      >
        <div className="demo-frame-shell">
          <PreviewAppChrome
            activeNav={activeNav}
            breadcrumb={breadcrumb}
            title={title}
            toolbar={toolbar}
            className="h-full"
          >
            <DemoViewport>{children}</DemoViewport>
          </PreviewAppChrome>
        </div>
      </div>
    </PreviewModeProvider>
  )
}

/** @deprecated Use `DemoFrame` — kept for transitional imports */
export const ProductShell = DemoFrame
