import { Link } from '@tanstack/react-router'
import { LogOut } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { useLogout } from '@/features/auth/use-auth'
import { NAV_ITEMS } from '@/lib/navigation'
import { cn } from '@/lib/utils'

export function AppSidebar({ className }: { className?: string }) {
  const logout = useLogout()

  return (
    <aside
      className={cn(
        'flex h-full min-h-0 w-64 flex-col border-r bg-card/50 p-4',
        className,
      )}
    >
      <div className="mb-6 px-2">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Math Assistant
        </p>
        <h1 className="text-lg font-bold">Platform</h1>
      </div>

      <nav className="flex flex-1 flex-col gap-1">
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <Link
            key={to}
            to={to}
            className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground [&.active]:bg-accent [&.active]:text-accent-foreground"
          >
            <Icon className="h-4 w-4" />
            {label}
          </Link>
        ))}
      </nav>

      <Separator className="my-4" />
      <Button
        variant="ghost"
        className="justify-start"
        onClick={() => logout.mutate()}
      >
        <LogOut className="h-4 w-4" />
        Sign out
      </Button>
    </aside>
  )
}
