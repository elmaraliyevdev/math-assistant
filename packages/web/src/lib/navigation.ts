import type { LucideIcon } from 'lucide-react'
import {
  Bot,
  Film,
  FlaskConical,
  Gamepad2,
  LayoutDashboard,
  LayoutTemplate,
  Settings,
  Sigma,
} from 'lucide-react'

export interface NavItem {
  to: string
  label: string
  icon: LucideIcon
}

/** Primary app navigation — workspace-first, minimal chrome */
export const NAV_ITEMS: NavItem[] = [
  { to: '/dashboard', label: 'Workspace', icon: LayoutDashboard },
  { to: '/games', label: 'Games', icon: Gamepad2 },
  { to: '/reel-studio', label: 'Studio', icon: Film },
  { to: '/simulations', label: 'Simulations', icon: FlaskConical },
  { to: '/assistant', label: 'AI Assistant', icon: Bot },
  { to: '/settings', label: 'Settings', icon: Settings },
]

/** Secondary workspace tools */
export const SETTINGS_LINKS: NavItem[] = [
  { to: '/templates', label: 'Templates', icon: LayoutTemplate },
  { to: '/mathematics', label: 'Mathematics', icon: Sigma },
]
