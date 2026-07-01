import { Link, useRouterState } from '@tanstack/react-router'
import { ChevronRight } from 'lucide-react'

import { MobileNav } from '@/components/mobile-nav'
import { buildBreadcrumbs } from '@/lib/breadcrumbs'
import { cn } from '@/lib/utils'

export function AppHeader({ className }: { className?: string }) {
  const pathname = useRouterState({ select: (state) => state.location.pathname })
  const isStudio = pathname.includes('/reel-studio')
  const breadcrumbs = buildBreadcrumbs(pathname)
  const pageTitle = breadcrumbs[breadcrumbs.length - 1]?.label
  const showBreadcrumbs = breadcrumbs.length > 0

  if (isStudio) {
    return (
      <header className="flex h-12 shrink-0 items-center border-b border-border/20 px-4 md:hidden">
        <MobileNav />
      </header>
    )
  }

  if (!showBreadcrumbs) {
    return (
      <header
        className={cn(
          'flex h-16 shrink-0 items-center border-b border-border/40 px-4 md:hidden md:px-6',
          className,
        )}
      >
        <MobileNav />
      </header>
    )
  }

  return (
    <header
      className={cn(
        'flex h-16 shrink-0 items-center gap-4 border-b border-border/40 px-4 md:px-6',
        className,
      )}
    >
      <div className="flex min-w-0 flex-1 items-center gap-3">
        <MobileNav />
        <nav aria-label="Breadcrumb" className="hidden min-w-0 sm:block">
          <ol className="flex items-center gap-1 text-sm text-muted-foreground">
            {breadcrumbs.map((item, index) => {
              const isLast = index === breadcrumbs.length - 1
              return (
                <li key={`${item.label}-${index}`} className="flex min-w-0 items-center gap-1">
                  {index > 0 ? (
                    <ChevronRight className="h-3.5 w-3.5 shrink-0 opacity-50" aria-hidden />
                  ) : null}
                  {item.path && !isLast ? (
                    <Link
                      to={item.path}
                      className="truncate transition-colors duration-200 hover:text-foreground"
                    >
                      {item.label}
                    </Link>
                  ) : (
                    <span
                      className={cn(
                        'truncate',
                        isLast ? 'font-medium text-foreground' : '',
                      )}
                    >
                      {item.label}
                    </span>
                  )}
                </li>
              )
            })}
          </ol>
        </nav>
        {pageTitle ? (
          <p className="truncate text-sm font-medium sm:hidden">{pageTitle}</p>
        ) : null}
      </div>
    </header>
  )
}
