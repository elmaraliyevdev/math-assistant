import { Outlet, useRouterState } from '@tanstack/react-router'

import { AppHeader } from '@/components/app-header'
import { AppSidebar } from '@/components/app-sidebar'
import { ErrorBoundary } from '@/components/error-boundary'
import { useMe, useResendVerification } from '@/features/auth/use-auth'
import {
  SessionExpiryNotice,
  useSessionExpiryFromToken,
} from '@/features/auth/SessionExpiryNotice'
import { DemoModeBanner } from '@/features/demo/DemoModeBanner'
import { useSyncOrganization } from '@/hooks/use-sync-organization'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

export function AppLayout() {
  const { data: me } = useMe()
  const resend = useResendVerification()
  const expiresIn = useSessionExpiryFromToken()
  useSyncOrganization()
  const pathname = useRouterState({ select: (state) => state.location.pathname })
  const isImmersiveStudio = /\/versions\/[^/]+\/reel-studio/.test(pathname)

  return (
    <ErrorBoundary>
      <div className="flex h-screen overflow-hidden bg-background">
        {!isImmersiveStudio ? <AppSidebar className="hidden shrink-0 md:flex" /> : null}
        <div className="flex min-w-0 flex-1 flex-col">
          {!isImmersiveStudio ? <AppHeader /> : null}
          {me && me.user.emailVerified === false && !isImmersiveStudio && (
            <div className="border-b bg-amber-50 px-4 py-2 text-sm text-amber-900 dark:bg-amber-950 dark:text-amber-100 md:px-6">
              Please verify your email.
              <Button
                variant="ghost"
                className="h-auto p-0 pl-1 text-amber-900 dark:text-amber-100"
                disabled={resend.isPending}
                onClick={() => resend.mutate()}
              >
                Resend verification
              </Button>
            </div>
          )}
          <main
            className={cn(
              'flex-1 overflow-auto',
              !isImmersiveStudio && 'p-4 md:p-6',
              isImmersiveStudio && 'overflow-hidden p-0',
            )}
          >
            {expiresIn !== null && expiresIn > 0 && !isImmersiveStudio && (
              <SessionExpiryNotice expiresInSeconds={expiresIn} />
            )}
            {!isImmersiveStudio ? <DemoModeBanner /> : null}
            <Outlet />
          </main>
        </div>
      </div>
    </ErrorBoundary>
  )
}
