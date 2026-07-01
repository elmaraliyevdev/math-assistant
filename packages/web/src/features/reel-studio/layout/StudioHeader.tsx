import { Link } from '@tanstack/react-router'
import { Calculator, Home } from 'lucide-react'

import { ReelSetSelector } from '@/features/reel-studio/components/ReelSetSelector'
import { Button } from '@/components/ui/button'

export function StudioHeader({
  gameId,
  versionId,
  gameName,
  versionNumber,
}: {
  gameId: string
  versionId: string
  gameName: string
  versionNumber: number
}) {
  return (
    <header className="studio-toolbar flex h-14 shrink-0 items-center gap-3 border-b border-border/20 px-4 md:px-5">
      <Button variant="ghost" size="icon" className="h-8 w-8 shrink-0" asChild title="Studio home">
        <Link to="/reel-studio">
          <Home className="h-4 w-4" />
          <span className="sr-only">Studio home</span>
        </Link>
      </Button>
      <div className="min-w-0 flex-1">
        <nav className="text-xs text-muted-foreground" aria-label="Breadcrumb">
          <Link to="/reel-studio" className="transition-colors duration-150 hover:text-foreground">
            Studio
          </Link>
          <span className="mx-2">/</span>
          <Link
            to="/games/$gameId"
            params={{ gameId }}
            className="transition-colors duration-150 hover:text-foreground"
          >
            {gameName}
          </Link>
          <span className="mx-2">/</span>
          <span className="text-foreground/80">v{versionNumber}</span>
        </nav>
        <div className="mt-1 flex min-w-0 flex-wrap items-baseline gap-x-3 gap-y-0">
          <h1 className="truncate text-base font-semibold tracking-tight">{gameName}</h1>
          <span className="hidden text-muted-foreground/40 sm:inline">·</span>
          <div className="hidden sm:block">
            <ReelSetSelector variant="text" />
          </div>
        </div>
      </div>
      <Button variant="outline" size="sm" className="hidden h-8 shrink-0 sm:flex" asChild>
        <Link
          to="/mathematics"
          search={{ gameId, gameVersionId: versionId }}
        >
          <Calculator className="mr-1.5 h-3.5 w-3.5" />
          Mathematics
        </Link>
      </Button>
    </header>
  )
}
