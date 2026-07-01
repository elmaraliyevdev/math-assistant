import type { ReactNode } from 'react'

import { cn } from '../lib/cn'

/** Shared viewport height (px) — keep in sync with `--demo-viewport-height` in demo-frame.css */
export const DEMO_VIEWPORT_HEIGHT_PX = 580

export type DemoViewportProps = {
  children: ReactNode
  className?: string
}

/**
 * Fixed-size application viewport for all landing demos.
 * Width, height, scale, and clipping are controlled globally via CSS variables.
 */
export function DemoViewport({ children, className }: DemoViewportProps) {
  return (
    <div className={cn('demo-viewport', className)}>
      <div className="demo-viewport-inner">
        <div className="demo-viewport-content">{children}</div>
      </div>
    </div>
  )
}
