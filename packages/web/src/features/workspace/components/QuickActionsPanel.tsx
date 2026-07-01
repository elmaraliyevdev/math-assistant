import { Link } from '@tanstack/react-router'
import {
  BarChart3,
  Dices,
  FileUp,
  FlaskConical,
  Gamepad2,
  LayoutTemplate,
} from 'lucide-react'

import { WorkspacePanel } from '@/features/workspace/components/WorkspacePanel'
import { cn } from '@/lib/utils'

const ACTIONS = [
  { to: '/games/create', label: 'Create game', icon: Gamepad2 },
  { to: '/templates', label: 'Create template', icon: LayoutTemplate },
  { to: '/simulations/create', label: 'Run simulation', icon: FlaskConical },
  { to: '/reel-studio', label: 'Open reel studio', icon: Dices },
  { to: '/games', label: 'Import game', icon: FileUp },
  { to: '/simulations', label: 'Browse reports', icon: BarChart3 },
] as const

export function QuickActionsPanel() {
  return (
    <WorkspacePanel title="Quick actions">
      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {ACTIONS.map((action) => (
          <Link
            key={action.to}
            to={action.to}
            className={cn(
              'flex items-center gap-3 rounded-xl border border-border bg-background px-4 py-3.5 text-sm font-medium',
              'transition-colors hover:border-primary/30 hover:bg-primary/5',
            )}
          >
            <action.icon className="h-4 w-4 shrink-0 text-primary" />
            {action.label}
          </Link>
        ))}
      </div>
    </WorkspacePanel>
  )
}
