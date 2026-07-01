import { Link } from '@tanstack/react-router'
import { Sparkles } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { WorkspacePanel } from '@/features/workspace/components/WorkspacePanel'
import type { CopilotInsight } from '@/features/workspace/lib/workspace-copilot'

export function AiCopilotPanel({
  loading,
  insights,
}: {
  loading: boolean
  insights: CopilotInsight[]
}) {
  if (loading) {
    return (
      <WorkspacePanel title="AI Copilot">
        <div className="space-y-2">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-5/6" />
          <Skeleton className="h-4 w-4/6" />
        </div>
      </WorkspacePanel>
    )
  }

  return (
    <WorkspacePanel
      title={
        <span className="inline-flex items-center gap-2 text-2xl font-semibold tracking-tight">
          <Sparkles className="h-5 w-5 text-primary" />
          AI Copilot
        </span>
      }
    >
      <p className="mb-3 text-sm text-muted-foreground">I analyzed your workspace.</p>
      <ul className="space-y-2 text-sm">
        {insights.map((insight) => (
          <li key={insight.id} className="flex gap-2">
            <span className="text-muted-foreground">•</span>
            <span>{insight.text}</span>
          </li>
        ))}
      </ul>
      <Button variant="secondary" className="mt-4" asChild>
        <Link to="/assistant">Review recommendations</Link>
      </Button>
    </WorkspacePanel>
  )
}
