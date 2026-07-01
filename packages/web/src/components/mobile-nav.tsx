import { Link } from '@tanstack/react-router'
import { Menu } from 'lucide-react'
import { useState } from 'react'

import { Logo } from '@/components/logo'
import { SidebarHelpLinks, SidebarUserMenu } from '@/components/sidebar-user-menu'
import { NotificationCenter } from '@/features/notifications/components/NotificationCenter'
import { NAV_ITEMS, SETTINGS_LINKS } from '@/lib/navigation'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
} from '@/components/ui/dialog'
import { cn } from '@/lib/utils'

export function MobileNav() {
  const [open, setOpen] = useState(false)

  return (
    <>
      <Button
        variant="ghost"
        size="icon"
        className="md:hidden"
        aria-label="Open navigation menu"
        onClick={() => setOpen(true)}
      >
        <Menu className="h-5 w-5" />
      </Button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent
          className={cn(
            'fixed inset-y-0 left-0 top-0 flex h-full w-[min(100%,18rem)] max-w-none translate-x-0 translate-y-0 flex-col rounded-none border-r p-0',
            'data-[state=open]:animate-in data-[state=closed]:animate-out',
          )}
        >
          <DialogHeader className="border-b px-4 py-4 text-left">
            <Logo variant="full" to={null} />
            <p className="text-sm text-muted-foreground">Navigation</p>
          </DialogHeader>

          <nav className="flex flex-col gap-0.5 overflow-y-auto p-3" aria-label="Main">
            {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
              <Link
                key={to}
                to={to}
                onClick={() => setOpen(false)}
                className="flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted/50 hover:text-foreground [&.active]:bg-muted [&.active]:text-foreground"
              >
                <Icon className="h-4 w-4" />
                {label}
              </Link>
            ))}
          </nav>

          <div className="px-3 pb-2">
            <p className="px-3 pb-1 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
              Workspace tools
            </p>
            {SETTINGS_LINKS.map(({ to, label, icon: Icon }) => (
              <Link
                key={to}
                to={to}
                onClick={() => setOpen(false)}
                className="flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-muted/50 hover:text-foreground [&.active]:bg-muted [&.active]:text-foreground"
              >
                <Icon className="h-4 w-4 opacity-70" />
                {label}
              </Link>
            ))}
          </div>

          <div className="mt-auto space-y-2 border-t p-3">
            <SidebarHelpLinks />
            <NotificationCenter variant="sidebar" />
            <SidebarUserMenu />
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}
