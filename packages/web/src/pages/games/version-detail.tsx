import { Link, useParams } from '@tanstack/react-router'
import { Download, Film, FlaskConical, Sigma } from 'lucide-react'
import { useState } from 'react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import {
  CopyHashButton,
  JsonViewer,
  ValidationFindingsTable,
} from '@/features/games/components'
import { useGame, useGameVersion } from '@/features/games/hooks/use-games'
import { extractMathConfigSnapshot } from '@/features/simulations/utils/workbench'
import { formatDate } from '@/lib/utils'
import { exportsApi } from '@/services/exports'
import { toast } from '@/lib/toast'

export function GameVersionDetailPage() {
  const { gameId, versionId } = useParams({ strict: false }) as {
    gameId: string
    versionId: string
  }
  const game = useGame(gameId)
  const version = useGameVersion(gameId, versionId)
  const [exporting, setExporting] = useState(false)

  if (game.isLoading || version.isLoading) {
    return <Skeleton className="h-64 w-full" />
  }

  if (!game.data || !version.data) {
    return <p className="text-muted-foreground">Version not found.</p>
  }

  const detail = version.data
  const mathSnapshot = extractMathConfigSnapshot(detail.canonicalJson)

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm text-muted-foreground">
            <Link to="/games/$gameId" params={{ gameId }} className="hover:underline">
              {game.data.name}
            </Link>
          </p>
          <h2 className="text-2xl font-bold tracking-tight">Version {detail.version}</h2>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button asChild>
            <Link
              to="/simulations/create"
              search={{ gameVersionId: versionId }}
            >
              <FlaskConical className="h-4 w-4" />
              Run simulation
            </Link>
          </Button>
          <Button variant="secondary" asChild>
            <Link
              to="/games/$gameId/versions/$versionId/reel-studio"
              params={{ gameId, versionId }}
            >
              <Film className="h-4 w-4" />
              Open Reel Studio
            </Link>
          </Button>
          <Button variant="secondary" asChild>
            <Link
              to="/mathematics"
              search={{ gameId, gameVersionId: versionId }}
            >
              <Sigma className="h-4 w-4" />
              View mathematics
            </Link>
          </Button>
          <Button
            variant="outline"
            disabled={exporting}
            onClick={async () => {
              setExporting(true)
              try {
                await exportsApi.downloadGameVersion(gameId, versionId)
                toast.success('Version exported')
              } catch {
                toast.error('Export failed')
              } finally {
                setExporting(false)
              }
            }}
          >
            <Download className="h-4 w-4" />
            Export JSON
          </Button>
          <CopyHashButton hash={detail.contentHash} />
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Metadata</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-3">
          <div>
            <p className="text-sm text-muted-foreground">Version</p>
            <Badge variant="secondary">v{detail.version}</Badge>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Engine version</p>
            <p className="font-medium">{detail.engineVersion}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Created</p>
            <p className="font-medium">{formatDate(detail.createdAt)}</p>
          </div>
          {mathSnapshot.rtpTarget && (
            <div>
              <p className="text-sm text-muted-foreground">RTP target</p>
              <p className="font-medium">
                {mathSnapshot.rtpTarget.percent}%
                {mathSnapshot.rtpTarget.tolerance != null &&
                  ` ± ${mathSnapshot.rtpTarget.tolerance}%`}
              </p>
            </div>
          )}
          <div className="sm:col-span-3">
            <p className="text-sm text-muted-foreground">Content hash</p>
            <p className="break-all font-mono text-xs">{detail.contentHash}</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Validation summary</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Passed</p>
              <Badge variant={detail.validationSummary.passed ? 'success' : 'danger'}>
                {detail.validationSummary.passed ? 'Yes' : 'No'}
              </Badge>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total findings</p>
              <p className="text-lg font-semibold">
                {detail.validationSummary.findingCount}
              </p>
            </div>
          </div>
          <ValidationFindingsTable
            findings={detail.validationSummary.findings}
            emptyMessage="No findings — this version passed validation when created."
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Canonical JSON</CardTitle>
        </CardHeader>
        <CardContent>
          <JsonViewer value={detail.canonicalJson} />
        </CardContent>
      </Card>

      <Button variant="outline" asChild>
        <Link to="/games/$gameId" params={{ gameId }}>
          Back to game
        </Link>
      </Button>
    </div>
  )
}
