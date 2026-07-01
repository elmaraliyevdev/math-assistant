import { useCallback, useEffect, useRef, useState } from 'react'

import { cn } from '@/lib/utils'
import type { BottomDrawerTab } from '@/features/reel-studio/layout/types'
import { loadDockHeight, saveDockHeight } from '@/features/reel-studio/layout/types'

const TABS: Array<{ id: BottomDrawerTab; label: string }> = [
  { id: 'validation', label: 'Validation' },
  { id: 'simulation', label: 'Simulation' },
  { id: 'statistics', label: 'Statistics' },
  { id: 'console', label: 'Console' },
]

const TAB_BAR_HEIGHT = 32
const RESIZE_HANDLE_HEIGHT = 8

export function StudioBottomDock({
  activeTab,
  onTabChange,
  validation,
  simulation,
  statistics,
  console: consolePanel,
}: {
  activeTab: BottomDrawerTab | null
  onTabChange: (tab: BottomDrawerTab | null) => void
  validation: React.ReactNode
  simulation: React.ReactNode
  statistics: React.ReactNode
  console: React.ReactNode
}) {
  const [height, setHeight] = useState(loadDockHeight)
  const resizing = useRef(false)
  const startY = useRef(0)
  const startHeight = useRef(0)

  const content =
    activeTab === 'validation'
      ? validation
      : activeTab === 'simulation'
        ? simulation
        : activeTab === 'statistics'
          ? statistics
          : activeTab === 'console'
            ? consolePanel
            : null

  const isOpen = Boolean(content)
  const contentHeight = isOpen ? height - TAB_BAR_HEIGHT - RESIZE_HANDLE_HEIGHT : 0

  useEffect(() => {
    if (isOpen) saveDockHeight(height)
  }, [height, isOpen])

  const onResizeStart = useCallback(
    (event: React.PointerEvent) => {
      resizing.current = true
      startY.current = event.clientY
      startHeight.current = height
      event.currentTarget.setPointerCapture(event.pointerId)
    },
    [height],
  )

  const onResizeMove = useCallback((event: React.PointerEvent) => {
    if (!resizing.current) return
    const delta = startY.current - event.clientY
    setHeight(Math.min(480, Math.max(160, startHeight.current + delta)))
  }, [])

  const onResizeEnd = useCallback((event: React.PointerEvent) => {
    resizing.current = false
    event.currentTarget.releasePointerCapture(event.pointerId)
  }, [])

  return (
    <div
      className={cn('studio-bottom-dock flex shrink-0 flex-col bg-background', isOpen && 'border-t border-border/20')}
      style={{ height: isOpen ? height : TAB_BAR_HEIGHT }}
    >
      {isOpen ? (
        <div
          role="separator"
          aria-orientation="horizontal"
          className="group flex shrink-0 cursor-row-resize items-center justify-center"
          style={{ height: RESIZE_HANDLE_HEIGHT }}
          onPointerDown={onResizeStart}
          onPointerMove={onResizeMove}
          onPointerUp={onResizeEnd}
        >
          <div className="h-1 w-12 rounded-full bg-border/60 transition-colors duration-150 group-hover:bg-primary/40" />
        </div>
      ) : null}

      <div className="flex shrink-0 items-center gap-1 overflow-x-auto px-4" style={{ height: TAB_BAR_HEIGHT }}>
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => onTabChange(activeTab === tab.id ? null : tab.id)}
            className={cn(
              'shrink-0 rounded-md px-3 py-1.5 text-xs font-medium transition-colors duration-150',
              activeTab === tab.id
                ? 'bg-primary/10 text-primary'
                : 'text-muted-foreground hover:bg-muted/50 hover:text-foreground',
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {isOpen ? (
        <div className="min-h-0 flex-1 overflow-y-auto px-4 pb-4" style={{ height: contentHeight }}>
          {content}
        </div>
      ) : null}
    </div>
  )
}
