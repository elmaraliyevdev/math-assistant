import {
  BarChart3,
  Calculator,
  Layers,
  Settings2,
  Shield,
} from 'lucide-react'
import type { ReactNode } from 'react'

import logoWhiteUrl from '@/assets/brand/logo-white.svg'
import { cn } from '@/lib/utils'

import { usePreviewMode } from './preview-mode-context'

export type PreviewNavId =
  | 'games'
  | 'reel-studio'
  | 'simulations'
  | 'mathematics'
  | 'certification'

const PREVIEW_NAV: Array<{
  id: PreviewNavId
  label: string
  icon: typeof Layers
}> = [
  { id: 'games', label: 'Games', icon: Layers },
  { id: 'reel-studio', label: 'Reel Studio', icon: Settings2 },
  { id: 'simulations', label: 'Simulations', icon: BarChart3 },
  { id: 'mathematics', label: 'Mathematics', icon: Calculator },
  { id: 'certification', label: 'Certification', icon: Shield },
]

export function PreviewAppChrome({
  activeNav = 'reel-studio',
  breadcrumb,
  title,
  toolbar,
  children,
  className,
}: {
  activeNav?: PreviewNavId
  breadcrumb?: string
  title?: string
  toolbar?: ReactNode
  children: ReactNode
  className?: string
}) {
  const { previewMode } = usePreviewMode()

  return (
    <div
      className={cn(
        'flex h-full min-h-0 overflow-hidden bg-background text-foreground',
        previewMode && 'pointer-events-none select-none',
        className,
      )}
      aria-hidden={previewMode || undefined}
    >
      <aside className="hidden h-full w-60 shrink-0 flex-col border-r border-border/40 bg-background/95 p-3 md:flex">
        <div className="mb-4 px-2 pt-1">
          <img
            src={logoWhiteUrl}
            alt="MathStudio"
            className="h-6 w-auto max-w-[10rem]"
          />
        </div>
        <nav className="flex flex-col gap-0.5" aria-label="Main">
          {PREVIEW_NAV.map(({ id, label, icon: Icon }) => (
            <div
              key={id}
              className={cn(
                'flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                activeNav === id
                  ? 'bg-muted text-foreground'
                  : 'text-muted-foreground',
              )}
            >
              <Icon className="h-4 w-4 shrink-0" />
              {label}
            </div>
          ))}
        </nav>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-12 shrink-0 items-center justify-between gap-3 border-b border-border/40 px-4 md:px-6">
          <div className="min-w-0 truncate text-sm text-muted-foreground">
            {breadcrumb}
          </div>
          {toolbar ? <div className="shrink-0">{toolbar}</div> : null}
        </header>
        {title ? (
          <div className="border-b border-border/30 px-4 py-2 md:px-6">
            <h2 className="text-sm font-semibold tracking-tight">{title}</h2>
          </div>
        ) : null}
        <div className="min-h-0 flex-1 overflow-hidden bg-background p-0">
          {children}
        </div>
      </div>
    </div>
  )
}
