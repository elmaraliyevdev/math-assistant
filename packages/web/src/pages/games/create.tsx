import { Link } from '@tanstack/react-router'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { GameForm } from '@/features/games/components'
import { useCreateGame } from '@/features/games/hooks/use-games'
import { useCurrentOrganization } from '@/hooks/use-sync-organization'
import { useOrganizationStore } from '@/stores/organization-store'

export function GameCreatePage() {
  const createGame = useCreateGame()
  const currentOrg = useCurrentOrganization()
  const organizationId = useOrganizationStore((state) => state.currentOrganizationId)

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Create game</h2>
        <p className="text-muted-foreground">
          Creating in {currentOrg?.organizationName ?? 'your organization'}.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Game details</CardTitle>
        </CardHeader>
        <CardContent>
          <GameForm
            submitLabel="Create game"
            loading={createGame.isPending}
            onSubmit={(values) => {
              if (!organizationId) return
              createGame.mutate({
                ...values,
                organizationId,
              })
            }}
          />
          <Button variant="outline" className="mt-4" asChild>
            <Link to="/games">Cancel</Link>
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
