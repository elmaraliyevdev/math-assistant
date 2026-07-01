/**
 * @deprecated Workspace and theme controls moved to SidebarUserMenu (Phase 20).
 * This file is kept for backwards compatibility if imported elsewhere.
 */
export { SidebarUserMenu as OrganizationSwitcher } from '@/components/sidebar-user-menu'

/** @deprecated Use Preferences → Theme in the sidebar user menu */
export function ThemeToggle() {
  return null
}
