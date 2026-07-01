'use client'

import { useLayoutEffect, useRef, useState, type ReactNode } from 'react'

import { cn } from '../lib/cn'

import '../styles/demo-scale.css'

/** Canonical desktop width for hero three-column studio layout. */
export const DEMO_HERO_DESIGN_WIDTH = 832

/** Canonical desktop width for walkthrough spotlight previews. */
export const DEMO_SPOTLIGHT_DESIGN_WIDTH = 640

export type DemoScaleProps = {
  children: ReactNode
  className?: string
  /** Unscaled canvas width in CSS pixels at scale 1. */
  designWidth?: number
}

/**
 * Keeps demo UI identical across breakpoints — scales down to fit the container
 * instead of switching to alternate mobile layouts.
 */
export function DemoScale({
  children,
  className,
  designWidth = DEMO_SPOTLIGHT_DESIGN_WIDTH,
}: DemoScaleProps) {
  const rootRef = useRef<HTMLDivElement>(null)
  const canvasRef = useRef<HTMLDivElement>(null)
  const [layout, setLayout] = useState({ scale: 1, height: 0, width: designWidth })

  useLayoutEffect(() => {
    const root = rootRef.current
    const canvas = canvasRef.current
    if (!root || !canvas) return

    const update = () => {
      const available = root.clientWidth
      const scale = available > 0 ? Math.min(1, available / designWidth) : 1
      const height = canvas.offsetHeight * scale
      const width = designWidth * scale

      setLayout({ scale, height, width })
    }

    update()

    const rootObserver = new ResizeObserver(update)
    const canvasObserver = new ResizeObserver(update)

    rootObserver.observe(root)
    canvasObserver.observe(canvas)

    return () => {
      rootObserver.disconnect()
      canvasObserver.disconnect()
    }
  }, [designWidth])

  return (
    <div
      ref={rootRef}
      className={cn('demo-scale-root', className)}
      style={{ height: layout.height > 0 ? layout.height : undefined }}
    >
      <div
        className="demo-scale-align"
        style={{ width: layout.width }}
      >
        <div
          ref={canvasRef}
          className="demo-scale-canvas"
          style={{
            width: designWidth,
            transform: `scale(${layout.scale})`,
          }}
        >
          {children}
        </div>
      </div>
    </div>
  )
}
