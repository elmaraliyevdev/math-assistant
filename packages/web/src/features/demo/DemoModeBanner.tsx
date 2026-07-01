import { Link, useRouterState } from '@tanstack/react-router'
import { Eye } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { useDemoOverview } from '@/features/demo/use-demo'

const DEMO_ROUTES = ['/games', '/simulations', '/reel-studio', '/mathematics', '/assistant']

export function DemoModeBanner() {
  const pathname = useRouterState({ select: (s) => s.location.pathname })
  const { data: demo } = useDemoOverview(DEMO_ROUTES.some((route) => pathname.startsWith(route)))

  if (!demo?.configured || demo.gameCount === 0) {
    return null
  }

  return (
    <div className="mb-4 flex flex-wrap items-center justify-between gap-2 rounded-lg border border-amber-200 bg-amber-50 px-4 py-2 text-sm text-amber-900 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-100">
      <div className="flex items-center gap-2">
        <Badge variant="outline" className="gap-1 border-amber-300 bg-background">
          <Eye className="h-3 w-3" />
          Demo available
        </Badge>
        <span>
          Explore <strong>{demo.organizationName}</strong> — {demo.gameCount} games with
          simulations and reports (read-only).
        </span>
      </div>
      <Button variant="outline" size="sm" asChild>
        <Link to="/demo">Open demo</Link>
      </Button>
    </div>
  )
}
