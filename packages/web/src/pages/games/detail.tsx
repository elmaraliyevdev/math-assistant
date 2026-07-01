import { Link, useParams } from '@tanstack/react-router'
import { Layers, Pencil, Plus, Trash2 } from 'lucide-react'
import { useMemo, useState } from 'react'

import {
  ActionBar,
  EmptyState,
  InfoGrid,
  MetricCard,
  PageHeader,
  PageLayout,
  PageSection,
  SectionHeader,
  StatusBadge,
  toneForProjectStatus,
  VersionCard,
} from '@/components/design-system'
import { ConfirmDialog } from '@/components/ui/confirm-dialog'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { JsonViewer, VersionUploadDialog } from '@/features/games/components'
import { GameEditDialog } from '@/features/games/components/GameEditDialog'
import { useDashboardSummary } from '@/features/dashboard/hooks/use-dashboard'
import {
  deriveGameStatus,
  deriveVersionStatus,
  gameStatusLabel,
  versionDesignHealth,
} from '@/features/games/lib/game-status'
import {
  useDeleteGame,
  useGame,
  useGameVersion,
  useGameVersions,
} from '@/features/games/hooks/use-games'
import { getLatestVersion, simulationsForGame } from '@/features/workspace/lib/workspace-status'
import type { GameVersionSummary } from '@/types/api'
import { formatRelativeTime } from '@/lib/format-relative-time'
import { formatPercent } from '@/lib/utils'

function JsonPreviewDialog({
  gameId,
  version,
  onClose,
}: {
  gameId: string
  version: GameVersionSummary
  onClose: () => void
}) {
  const detail = useGameVersion(gameId, version.id)
  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>Version {version.version} — canonical JSON</DialogTitle>
        </DialogHeader>
        {detail.isLoading && <Skeleton className="h-48 w-full" />}
        {detail.data && <JsonViewer value={detail.data.canonicalJson} />}
      </DialogContent>
    </Dialog>
  )
}

function ComingSoonTab({ title, description }: { title: string; description: string }) {
  return (
    <EmptyState
      icon={Layers}
      title={title}
      description={description}
    />
  )
}

export function GameDetailPage() {
  const { gameId } = useParams({ strict: false }) as { gameId: string }
  const game = useGame(gameId)
  const versions = useGameVersions(gameId)
  const summary = useDashboardSummary()
  const deleteGame = useDeleteGame()
  const [uploadOpen, setUploadOpen] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)
  const [editOpen, setEditOpen] = useState(false)
  const [jsonPreview, setJsonPreview] = useState<GameVersionSummary | null>(null)
  const [tab, setTab] = useState('overview')

  const versionList = versions.data ?? []
  const recentSimulations = summary.data?.recentSimulations ?? []

  const gameSimulations = useMemo(() => {
    const versionIds = versionList.map((version) => version.id)
    return simulationsForGame(versionIds, recentSimulations)
  }, [versionList, recentSimulations])

  const heroMeta = useMemo(() => {
    const status = deriveGameStatus(versionList, recentSimulations)
    const latestVersion = getLatestVersion(versionList)
    const latestSim = gameSimulations[0] ?? null
    const versionStatus = latestVersion
      ? deriveVersionStatus(latestVersion, latestVersion, latestSim)
      : null

    return {
      status,
      statusLabel: gameStatusLabel(status, versionList, recentSimulations),
      designHealth: versionStatus
        ? versionDesignHealth(versionStatus, latestSim)
        : null,
      engineVersion: latestVersion?.engineVersion ?? null,
      lastRtp: latestSim?.rtp ?? null,
      lastSimulationAt: latestSim?.createdAt ?? null,
    }
  }, [versionList, recentSimulations, gameSimulations])

  if (game.isLoading) {
    return (
      <PageLayout>
        <Skeleton className="mb-8 h-40 w-full rounded-xl" />
        <Skeleton className="h-64 w-full rounded-xl" />
      </PageLayout>
    )
  }

  if (!game.data) {
    return (
      <PageLayout>
        <p className="text-muted-foreground">Game not found.</p>
      </PageLayout>
    )
  }

  const latestVersion = getLatestVersion(versionList)
  const sortedVersions = [...versionList].sort((a, b) => b.version - a.version)
  const simByVersion = new Map(gameSimulations.map((item) => [item.gameVersionId, item]))

  return (
    <PageLayout>
      <nav className="mb-6 text-sm text-muted-foreground" aria-label="Breadcrumb">
        <Link to="/games" className="hover:text-foreground">
          Games
        </Link>
        <span className="mx-2">/</span>
        <span className="text-foreground">{game.data.name}</span>
      </nav>

      <PageHeader
        title={game.data.name}
        description={game.data.description ?? 'Slot game project'}
        actions={
          <ActionBar>
            <Button onClick={() => setUploadOpen(true)}>
              <Plus className="h-4 w-4" />
              New version
            </Button>
            <Button variant="outline" onClick={() => setEditOpen(true)}>
              <Pencil className="h-4 w-4" />
              Edit game
            </Button>
            <Button variant="destructive" onClick={() => setDeleteOpen(true)}>
              <Trash2 className="h-4 w-4" />
              Delete
            </Button>
          </ActionBar>
        }
      />

      <Card className="mb-8 shadow-none">
        <CardContent className="space-y-6 p-6">
          <div className="flex flex-wrap items-center gap-3">
            <StatusBadge
              label={heroMeta.statusLabel}
              tone={toneForProjectStatus(heroMeta.status)}
            />
            <span className="text-sm text-muted-foreground">
              Updated {formatRelativeTime(game.data.updatedAt)}
            </span>
            {heroMeta.engineVersion ? (
              <span className="text-sm text-muted-foreground">
                · Engine {heroMeta.engineVersion.replace('runtime-core@', 'runtime-core ')}
              </span>
            ) : null}
          </div>
          <InfoGrid>
            {heroMeta.designHealth != null ? (
              <MetricCard label="Design health" value={heroMeta.designHealth} />
            ) : null}
            <MetricCard label="Versions" value={versionList.length} />
            {heroMeta.lastRtp != null ? (
              <MetricCard label="Last RTP" value={formatPercent(heroMeta.lastRtp)} />
            ) : null}
            {heroMeta.lastSimulationAt ? (
              <MetricCard
                label="Last simulation"
                value={formatRelativeTime(heroMeta.lastSimulationAt)}
              />
            ) : null}
          </InfoGrid>
          {latestVersion ? (
            <div className="pt-2">
              <Button asChild>
                <Link
                  to="/games/$gameId/versions/$versionId/reel-studio"
                  params={{ gameId, versionId: latestVersion.id }}
                >
                  Continue in Studio
                </Link>
              </Button>
            </div>
          ) : null}
        </CardContent>
      </Card>

      <Tabs value={tab} onValueChange={setTab}>
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="versions">Versions</TabsTrigger>
          <TabsTrigger value="simulations">Simulations</TabsTrigger>
          <TabsTrigger value="certification">Certification</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <PageSection>
            <SectionHeader
              title="Version history"
              description="Continue designing or validate with simulation"
              action={
                <Button variant="outline" size="sm" onClick={() => setUploadOpen(true)}>
                  New version
                </Button>
              }
            />
            {versions.isLoading ? (
              <div className="space-y-4">
                {Array.from({ length: 2 }).map((_, index) => (
                  <Skeleton key={index} className="h-48 w-full rounded-xl" />
                ))}
              </div>
            ) : sortedVersions.length === 0 ? (
              <EmptyState
                icon={Layers}
                title="No versions yet"
                description="Create a version to start designing in the Mathematical Design Studio."
                action={
                  <Button onClick={() => setUploadOpen(true)}>New version</Button>
                }
              />
            ) : (
              <div className="grid gap-4">
                {sortedVersions.slice(0, 3).map((version) => {
                  const simulation = simByVersion.get(version.id) ?? null
                  const status = deriveVersionStatus(version, latestVersion, simulation)
                  return (
                    <VersionCard
                      key={version.id}
                      gameId={gameId}
                      version={version}
                      status={status}
                      health={versionDesignHealth(status, simulation)}
                      rtp={simulation?.rtp ?? null}
                      simulationStatus={simulation?.status ?? null}
                      isLatest={latestVersion?.id === version.id}
                      onViewJson={() => setJsonPreview(version)}
                    />
                  )
                })}
                {sortedVersions.length > 3 ? (
                  <Button variant="ghost" onClick={() => setTab('versions')}>
                    View all {sortedVersions.length} versions
                  </Button>
                ) : null}
              </div>
            )}
          </PageSection>
        </TabsContent>

        <TabsContent value="versions">
          <PageSection>
            {versions.isLoading ? (
              <div className="space-y-4">
                {Array.from({ length: 3 }).map((_, index) => (
                  <Skeleton key={index} className="h-48 w-full rounded-xl" />
                ))}
              </div>
            ) : sortedVersions.length === 0 ? (
              <EmptyState
                icon={Layers}
                title="No versions yet"
                description="Create a version to start designing."
                action={<Button onClick={() => setUploadOpen(true)}>New version</Button>}
              />
            ) : (
              <div className="grid gap-4">
                {sortedVersions.map((version) => {
                  const simulation = simByVersion.get(version.id) ?? null
                  const status = deriveVersionStatus(version, latestVersion, simulation)
                  return (
                    <VersionCard
                      key={version.id}
                      gameId={gameId}
                      version={version}
                      status={status}
                      health={versionDesignHealth(status, simulation)}
                      rtp={simulation?.rtp ?? null}
                      simulationStatus={simulation?.status ?? null}
                      isLatest={latestVersion?.id === version.id}
                      onViewJson={() => setJsonPreview(version)}
                    />
                  )
                })}
              </div>
            )}
          </PageSection>
        </TabsContent>

        <TabsContent value="simulations">
          <ComingSoonTab
            title="Simulations coming soon"
            description="Run and monitor simulation jobs for this game from this tab."
          />
        </TabsContent>

        <TabsContent value="certification">
          <ComingSoonTab
            title="Certification coming soon"
            description="Track certification readiness and approval workflows here."
          />
        </TabsContent>

        <TabsContent value="analytics">
          <ComingSoonTab
            title="Analytics coming soon"
            description="RTP trends, volatility insights, and performance analytics will live here."
          />
        </TabsContent>
      </Tabs>

      <VersionUploadDialog gameId={gameId} open={uploadOpen} onOpenChange={setUploadOpen} />
      <GameEditDialog game={game.data} open={editOpen} onOpenChange={setEditOpen} />
      <ConfirmDialog
        open={deleteOpen}
        onOpenChange={setDeleteOpen}
        title="Delete game"
        description={`Delete "${game.data.name}" and all versions?`}
        confirmLabel="Delete"
        destructive
        loading={deleteGame.isPending}
        onConfirm={() => deleteGame.mutate(gameId)}
      />
      {jsonPreview && (
        <JsonPreviewDialog
          gameId={gameId}
          version={jsonPreview}
          onClose={() => setJsonPreview(null)}
        />
      )}
    </PageLayout>
  )
}
