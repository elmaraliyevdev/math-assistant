import { Outlet } from '@tanstack/react-router'

import { AppSidebar } from '@/components/app-sidebar'
import { ErrorBoundary } from '@/components/error-boundary'
import { MobileNav } from '@/components/mobile-nav'
import {
  OrganizationSwitcher,
  ThemeToggle,
} from '@/components/organization-switcher'
import { NotificationCenter } from '@/features/notifications/components/NotificationCenter'
import { useMe } from '@/features/auth/use-auth'
import { useSyncOrganization } from '@/hooks/use-sync-organization'

export function AppLayout() {
  const { data: me } = useMe()
  useSyncOrganization()

  return (
    <ErrorBoundary>
      <div className="flex h-screen overflow-hidden bg-background">
        <AppSidebar className="hidden shrink-0 md:flex" />
        <div className="flex min-w-0 flex-1 flex-col">
          <header className="flex items-center justify-between gap-3 border-b px-4 py-3 md:px-6">
            <div className="flex min-w-0 items-center gap-3">
              <MobileNav />
              <div className="min-w-0">
                <p className="text-sm text-muted-foreground">Signed in as</p>
                <p className="truncate font-medium">{me?.user.fullName ?? me?.user.email}</p>
              </div>
            </div>
            <div className="flex shrink-0 items-center gap-2">
              <NotificationCenter />
              <OrganizationSwitcher />
              <ThemeToggle />
            </div>
          </header>
          <main className="flex-1 overflow-auto p-4 md:p-6">
            <Outlet />
          </main>
        </div>
      </div>
    </ErrorBoundary>
  )
}
