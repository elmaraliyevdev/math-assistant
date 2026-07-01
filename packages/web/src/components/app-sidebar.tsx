import { Link } from '@tanstack/react-router'

import { Logo } from '@/components/logo'
import { SidebarHelpLinks, SidebarUserMenu } from '@/components/sidebar-user-menu'
import { NotificationCenter } from '@/features/notifications/components/NotificationCenter'
import { NAV_ITEMS, SETTINGS_LINKS } from '@/lib/navigation'
import { cn } from '@/lib/utils'

export function AppSidebar({ className }: { className?: string }) {
  return (
    <aside
      className={cn(
        'flex h-full min-h-0 w-60 flex-col border-r border-border/40 bg-background/95 p-3',
        className,
      )}
    >
      <div className="mb-6 px-2 pt-2">
        <Logo variant="full" to="/dashboard" />
      </div>

      <nav className="flex flex-col gap-0.5" aria-label="Main">
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <Link
            key={to}
            to={to}
            className="flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition-colors duration-200 hover:bg-muted/50 hover:text-foreground [&.active]:bg-muted [&.active]:text-foreground"
          >
            <Icon className="h-4 w-4 shrink-0" />
            {label}
          </Link>
        ))}
      </nav>

      <div className="mt-6">
        <p className="px-3 pb-1 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
          Workspace tools
        </p>
        <nav className="flex flex-col gap-0.5" aria-label="Workspace tools">
          {SETTINGS_LINKS.map(({ to, label, icon: Icon }) => (
            <Link
              key={to}
              to={to}
              className="flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-muted-foreground transition-colors duration-200 hover:bg-muted/50 hover:text-foreground [&.active]:bg-muted [&.active]:text-foreground"
            >
              <Icon className="h-4 w-4 shrink-0 opacity-70" />
              {label}
            </Link>
          ))}
        </nav>
      </div>

      <div className="flex-1" />

      <SidebarHelpLinks className="mb-2" />
      <NotificationCenter variant="sidebar" className="mb-2" />
      <SidebarUserMenu />
    </aside>
  )
}
