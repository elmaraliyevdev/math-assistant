import { useNavigate } from '@tanstack/react-router'
import { Copy, Eye } from 'lucide-react'
import { useEffect } from 'react'
import { toast } from 'sonner'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { useDemoOverview, useDuplicateDemo } from '@/features/demo/use-demo'
import { trackEvent } from '@/lib/analytics'

const DEMO_GAMES = [
  'Classic Fruits',
  'Book of Riches',
  'Hold & Win Deluxe',
  'Aztec Adventure',
  'Treasure Spins',
]

export function DemoPage() {
  const navigate = useNavigate()
  const { data, isLoading } = useDemoOverview()
  const duplicate = useDuplicateDemo()

  useEffect(() => {
    trackEvent('demo_opened')
  }, [])

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="flex flex-wrap items-center gap-3">
        <h1 className="text-2xl font-bold">Demo Workspace</h1>
        <Badge variant="secondary" className="gap-1">
          <Eye className="h-3 w-3" />
          Read-only
        </Badge>
      </div>
      <p className="text-muted-foreground">
        Explore pre-loaded games, simulations, and reports. Duplicate into your
        workspace to start editing.
      </p>

      {isLoading ? (
        <div className="space-y-4">
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
        </div>
      ) : data?.configured ? (
        <>
          <Card>
            <CardHeader>
              <CardTitle>{data.organizationName}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                {data.gameCount} games · {data.simulationCount} simulations ·{' '}
                {data.versionCount} versions
              </p>
              <Button className="mt-4" onClick={() => navigate({ to: '/games' })}>
                Explore demo games
              </Button>
            </CardContent>
          </Card>

          <div className="grid gap-4 sm:grid-cols-2">
            {data.games.map((game) => (
              <Card key={game.id}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-base">{game.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-muted-foreground">
                    {game.versionCount} versions · {game.simulationCount} simulations
                  </p>
                  <Button
                    variant="ghost"
                    className="mt-1 h-auto p-0"
                    onClick={() =>
                      navigate({ to: '/games/$gameId', params: { gameId: game.id } })
                    }
                  >
                    View game →
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>

          <Card className="border-dashed border-primary/40 bg-primary/5">
            <CardContent className="flex flex-col items-start gap-4 pt-6 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="font-medium">Duplicate demo into my workspace</p>
                <p className="text-sm text-muted-foreground">
                  Copy all demo games and versions to your organization.
                </p>
              </div>
              <Button
                variant="outline"
                disabled={duplicate.isPending}
                onClick={() =>
                  duplicate.mutate(undefined, {
                    onSuccess: (result) => {
                      toast.success(`Copied ${result.gamesCopied} games to your workspace`)
                    },
                  })
                }
              >
                <Copy className="mr-2 h-4 w-4" />
                {duplicate.isPending ? 'Copying…' : 'Duplicate Demo'}
              </Button>
            </CardContent>
          </Card>
        </>
      ) : (
        <Card>
          <CardContent className="pt-6">
            <p className="text-muted-foreground">
              Demo workspace is being prepared. The following example games will be
              available:
            </p>
            <ul className="mt-4 list-inside list-disc text-sm">
              {DEMO_GAMES.map((name) => (
                <li key={name}>{name}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
