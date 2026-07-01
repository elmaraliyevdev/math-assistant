import { Link } from '@tanstack/react-router'
import { useMemo, useState } from 'react'
import {
  ArrowRight,
  Bot,
  FileJson,
  FlaskConical,
  FolderOpen,
  LayoutTemplate,
  Plus,
  Sparkles,
} from 'lucide-react'

import { ContinueWorkingCard } from '@/features/workspace/components/ContinueWorkingCard'
import { RecentSimulationsList } from '@/features/workspace/components/RecentSimulationsList'
import { useWorkspaceData } from '@/features/workspace/hooks/use-workspace-data'
import { Button } from '@/components/ui/button'
import { GAME_TEMPLATES } from '@/features/game-templates/api/templates-api'
import { CreatePresetDialog } from '@/features/reel-studio/landing/CreatePresetDialog'
import { JsonDropZone } from '@/features/reel-studio/landing/JsonDropZone'
import { OpenGameDialog } from '@/features/reel-studio/landing/OpenGameDialog'
import { StudioProjectCard } from '@/features/reel-studio/landing/StudioProjectCard'
import { getPinnedGameIds } from '@/features/reel-studio/lib/studio-pins'
import { Badge } from '@/components/ui/badge'

const STUDIO_AI_SUGGESTIONS = [
  { label: 'Improve RTP', prompt: 'How can I improve RTP for my current reel design?' },
  { label: 'Reduce volatility', prompt: 'Suggest ways to reduce volatility in a slot game' },
  { label: 'Explain reel balance', prompt: 'Explain reel balance and symbol distribution' },
  { label: 'Find symbol clustering', prompt: 'How do I detect symbol clustering on reels?' },
  { label: 'Optimize free spins', prompt: 'How to optimize free spin feature frequency?' },
]

const PINNED_TEMPLATES = ['simple-5x3', 'hold-win', 'free-spins']

export function StudioLandingPage() {
  const workspace = useWorkspaceData()
  const [openGame, setOpenGame] = useState(false)
  const [createOpen, setCreateOpen] = useState(false)
  const [pins, setPins] = useState(getPinnedGameIds)

  const pinnedProjects = useMemo(() => {
    const pinned = workspace.projects.filter((p) => pins.includes(p.game.id))
    const rest = workspace.projects.filter((p) => !pins.includes(p.game.id))
    return [...pinned, ...rest]
  }, [workspace.projects, pins])

  const templates = GAME_TEMPLATES.filter((t) => PINNED_TEMPLATES.includes(t.id))

  return (
    <div className="-mx-4 -mt-2 min-h-[calc(100vh-5rem)] space-y-8 md:-mx-6">
      <section className="border-b border-border/40 bg-gradient-to-b from-muted/30 to-transparent px-4 pb-8 pt-2 md:px-6">
        <div className="mx-auto max-w-6xl">
          <p className="text-xs font-medium uppercase tracking-wider text-primary">Reel Studio</p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight md:text-4xl">
            Mathematical Design Studio
          </h1>
          <p className="mt-3 max-w-2xl text-muted-foreground">
            Design reel strips, analyze symbol distribution, validate RTP, and iterate visually —
            like an IDE for slot mathematics.
          </p>
          <div className="mt-6 flex flex-wrap gap-2">
            <Button onClick={() => setOpenGame(true)}>
              <FolderOpen className="h-4 w-4" />
              Open game
            </Button>
            <Button variant="secondary" onClick={() => setCreateOpen(true)}>
              <Plus className="h-4 w-4" />
              New game
            </Button>
            <Button variant="outline" asChild>
              <Link to="/games/create">
                <FileJson className="h-4 w-4" />
                Import JSON
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link to="/templates">
                <LayoutTemplate className="h-4 w-4" />
                Browse templates
              </Link>
            </Button>
          </div>
        </div>
      </section>

      <div className="mx-auto grid max-w-6xl gap-6 px-4 md:px-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <ContinueWorkingCard
            loading={workspace.isLoading}
            hasGames={workspace.hasGames}
            meta={workspace.continueMeta}
          />

          <section>
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-lg font-semibold">Recent projects</h2>
              <Button variant="ghost" size="sm" asChild>
                <Link to="/games">View all</Link>
              </Button>
            </div>
            {pinnedProjects.length === 0 && !workspace.isLoading ? (
              <p className="rounded-lg border border-dashed p-8 text-center text-sm text-muted-foreground">
                No projects yet. Create a game to start designing reel strips.
              </p>
            ) : (
              <div className="space-y-2">
                {pinnedProjects.map((project) => (
                  <StudioProjectCard
                    key={project.game.id}
                    project={project}
                    pinned={pins.includes(project.game.id)}
                    onTogglePin={() => setPins(getPinnedGameIds())}
                  />
                ))}
              </div>
            )}
          </section>

          <JsonDropZone />
        </div>

        <div className="space-y-6">
          <section className="rounded-lg border border-border/60 p-4">
            <h2 className="text-sm font-semibold">Pinned templates</h2>
            <div className="mt-3 space-y-2">
              {templates.map((template) => (
                <Link
                  key={template.id}
                  to="/templates"
                  className="flex items-center justify-between rounded-md border px-3 py-2 text-sm transition-colors hover:bg-muted/50"
                >
                  <span>{template.name}</span>
                  <ArrowRight className="h-3.5 w-3.5 text-muted-foreground" />
                </Link>
              ))}
            </div>
          </section>

          <section className="rounded-lg border border-primary/20 bg-primary/5 p-4">
            <div className="mb-3 flex items-center gap-2">
              <Bot className="h-4 w-4 text-primary" />
              <h2 className="text-sm font-semibold">AI suggestions</h2>
            </div>
            <ul className="space-y-2">
              {STUDIO_AI_SUGGESTIONS.map((item) => (
                <li key={item.label}>
                  <Link
                    to="/assistant"
                    search={{ prompt: item.prompt }}
                    className="flex items-center gap-2 rounded-md px-2 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-background hover:text-foreground"
                  >
                    <Sparkles className="h-3.5 w-3.5 shrink-0 text-primary" />
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </section>

          <section>
            <div className="mb-3 flex items-center gap-2">
              <FlaskConical className="h-4 w-4 text-muted-foreground" />
              <h2 className="text-sm font-semibold">Recent activity</h2>
            </div>
            <div className="space-y-2 text-sm">
              {workspace.recentSimulations.slice(0, 3).map((sim) => (
                <div
                  key={sim.simulationId}
                  className="flex items-center justify-between rounded-md border px-3 py-2"
                >
                  <div className="min-w-0">
                    <p className="truncate font-medium">{sim.gameName ?? 'Simulation'}</p>
                    <p className="text-xs text-muted-foreground capitalize">{sim.status}</p>
                  </div>
                  <Badge variant="outline" className="shrink-0 capitalize">
                    {sim.status}
                  </Badge>
                </div>
              ))}
              {workspace.recentSimulations.length === 0 && !workspace.isLoading ? (
                <p className="text-xs text-muted-foreground">No recent simulations.</p>
              ) : null}
            </div>
          </section>

          <RecentSimulationsList
            loading={workspace.isLoading}
            simulations={workspace.recentSimulations}
          />
        </div>
      </div>

      <OpenGameDialog open={openGame} onOpenChange={setOpenGame} />
      <CreatePresetDialog open={createOpen} onOpenChange={setCreateOpen} />
    </div>
  )
}
