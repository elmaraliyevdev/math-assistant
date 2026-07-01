import { useMe } from '@/features/auth/use-auth'
import { PageLayout } from '@/components/design-system'
import { AiCopilotPanel } from '@/features/workspace/components/AiCopilotPanel'
import { ContinueWorkingCard } from '@/features/workspace/components/ContinueWorkingCard'
import { QuickActionsPanel } from '@/features/workspace/components/QuickActionsPanel'
import { RecentProjectsList } from '@/features/workspace/components/RecentProjectsList'
import { RecentSimulationsList } from '@/features/workspace/components/RecentSimulationsList'
import { WorkspaceHealthPanel } from '@/features/workspace/components/WorkspaceHealthPanel'
import { WorkspaceNotifications } from '@/features/workspace/components/WorkspaceNotifications'
import { useWorkspaceData } from '@/features/workspace/hooks/use-workspace-data'
import { workspaceGreeting } from '@/lib/format-relative-time'

export function DashboardPage() {
  const me = useMe()
  const workspace = useWorkspaceData()
  const displayName = me.data?.user.fullName?.trim() || me.data?.user.email || 'there'

  return (
    <PageLayout>
      <header className="mb-8 space-y-2">
        <h1 className="text-4xl font-bold tracking-tight">
          {workspaceGreeting(displayName)} 👋
        </h1>
        <p className="text-sm text-muted-foreground">Continue building your games.</p>
      </header>

      <div className="space-y-8">
        <ContinueWorkingCard
          loading={workspace.isLoading}
          hasGames={workspace.hasGames}
          meta={workspace.continueMeta}
        />

        <div className="grid gap-6 lg:grid-cols-2">
          <WorkspaceHealthPanel loading={workspace.isLoading} health={workspace.workspaceHealth} />
          <AiCopilotPanel loading={workspace.isLoading} insights={workspace.copilotInsights} />
        </div>

        <RecentProjectsList loading={workspace.isLoading} projects={workspace.projects} />
        <RecentSimulationsList
          loading={workspace.isLoading}
          simulations={workspace.recentSimulations}
        />
        <QuickActionsPanel />
        <WorkspaceNotifications
          loading={workspace.isLoading}
          notifications={workspace.notifications}
        />
      </div>
    </PageLayout>
  )
}
