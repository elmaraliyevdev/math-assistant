import type { LucideIcon } from 'lucide-react'
import {
  Building2,
  ClipboardList,
  Bot,
  FlaskConical,
  Gamepad2,
  LayoutDashboard,
  LayoutTemplate,
  Sigma,
  Settings,
} from 'lucide-react'

export interface NavItem {
  to: string
  label: string
  icon: LucideIcon
}

export const NAV_ITEMS: NavItem[] = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/games', label: 'Games', icon: Gamepad2 },
  { to: '/templates', label: 'Templates', icon: LayoutTemplate },
  { to: '/simulations', label: 'Simulations', icon: FlaskConical },
  { to: '/mathematics', label: 'Mathematics', icon: Sigma },
  { to: '/assistant', label: 'Assistant', icon: Bot },
  { to: '/audit', label: 'Audit', icon: ClipboardList },
  { to: '/organizations/settings', label: 'Organization', icon: Building2 },
  { to: '/settings', label: 'Settings', icon: Settings },
]
