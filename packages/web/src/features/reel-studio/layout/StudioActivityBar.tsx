import { Link } from '@tanstack/react-router'
import {
  Bot,
  FlaskConical,
  Layers,
  Palette,
  ShieldCheck,
  Sliders,
  Sparkles,
  Zap,
} from 'lucide-react'

import { StudioIcon } from '@/components/studio/StudioIcon'
import { Button } from '@/components/ui/button'
import type { BottomDrawerTab, WorkspaceMode } from '@/features/reel-studio/layout/types'
import { cn } from '@/lib/utils'

const ITEMS: Array<{
  id: WorkspaceMode | 'validation' | 'simulation'
  label: string
  icon: typeof Layers
  dock?: BottomDrawerTab
}> = [
  { id: 'design', label: 'Reels', icon: Layers },
  { id: 'symbols', label: 'Symbols', icon: Palette },
  { id: 'constraints', label: 'Constraints', icon: Sliders },
  { id: 'optimization', label: 'Optimize', icon: Zap },
  { id: 'validation', label: 'Validate', icon: ShieldCheck, dock: 'validation' },
  { id: 'simulation', label: 'Simulate', icon: FlaskConical, dock: 'simulation' },
  { id: 'ai', label: 'AI', icon: Bot },
]

export function StudioActivityBar({
  mode,
  onModeChange,
  onOpenDock,
}: {
  mode: WorkspaceMode
  onModeChange: (mode: WorkspaceMode) => void
  onOpenDock: (tab: BottomDrawerTab) => void
}) {
  return (
    <nav
      aria-label="Studio panels"
      className="flex w-12 shrink-0 flex-col items-center gap-1 border-r border-border/20 bg-muted/10 py-2"
    >
      {ITEMS.map((item) => {
        const isDock = 'dock' in item && item.dock
        const active = !isDock && mode === item.id
        return (
          <Button
            key={item.id}
            type="button"
            variant="ghost"
            size="icon"
            title={item.label}
            className={cn(
              'h-9 w-9 rounded-md',
              active && 'bg-primary/10 text-primary',
            )}
            onClick={() => {
              if (isDock && item.dock) {
                onOpenDock(item.dock)
                return
              }
              onModeChange(item.id as WorkspaceMode)
            }}
          >
            <StudioIcon icon={item.icon} />
            <span className="sr-only">{item.label}</span>
          </Button>
        )
      })}
      <div className="mt-auto flex flex-col gap-1">
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="h-9 w-9"
          title="Statistics"
          onClick={() => onOpenDock('statistics')}
        >
          <StudioIcon icon={Sparkles} />
        </Button>
      </div>
    </nav>
  )
}

export function StudioActivityBarMobile({
  mode,
  onModeChange,
}: {
  mode: WorkspaceMode
  onModeChange: (mode: WorkspaceMode) => void
}) {
  return (
    <div className="flex gap-1 overflow-x-auto border-b border-border/20 px-2 py-1 lg:hidden">
      {ITEMS.filter((item) => !item.dock).map((item) => (
        <Button
          key={item.id}
          type="button"
          variant={mode === item.id ? 'secondary' : 'ghost'}
          size="sm"
          className="h-8 shrink-0 text-xs"
          onClick={() => onModeChange(item.id as WorkspaceMode)}
        >
          {item.label}
        </Button>
      ))}
      <Button variant="ghost" size="sm" className="h-8 shrink-0 text-xs" asChild>
        <Link to="/assistant">AI</Link>
      </Button>
    </div>
  )
}
