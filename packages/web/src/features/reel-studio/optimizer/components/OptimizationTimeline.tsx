import { GitBranch, History } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useOptimizerStudio } from '@/features/reel-studio/optimizer/context/optimizer-context'

export function OptimizationTimeline() {
  const { history, selectIterationById, activeIteration } = useOptimizerStudio()

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm">
          <History className="h-4 w-4" />
          Optimization timeline
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {history.timeline.map((event) => (
          <button
            key={event.id}
            type="button"
            className={`flex w-full items-center justify-between rounded-md border px-3 py-2 text-left text-xs ${
              event.iterationId === activeIteration.id ? 'border-primary bg-primary/5' : ''
            }`}
            onClick={() => selectIterationById(event.iterationId)}
          >
            <span>
              {event.label} · {event.type}
            </span>
            <span className="text-muted-foreground">Health {event.health}</span>
          </button>
        ))}
      </CardContent>
    </Card>
  )
}

export function IterationSelector() {
  const { iterationChain, activeIteration, undoIteration, branchIteration } = useOptimizerStudio()

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm">
          <GitBranch className="h-4 w-4" />
          Iterations
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {iterationChain.map((iteration, index) => (
          <div key={iteration.id} className="flex items-center justify-between text-xs">
            <span>
              Iteration {index + 1} · {iteration.branchLabel} · Health {iteration.health}
            </span>
            {iteration.proposalTitle ? (
              <span className="text-muted-foreground">{iteration.proposalTitle}</span>
            ) : null}
          </div>
        ))}
        <div className="flex flex-wrap gap-2 pt-2">
          <Button type="button" size="sm" variant="outline" onClick={undoIteration}>
            Undo iteration
          </Button>
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={() => branchIteration(activeIteration.id, `B${iterationChain.length}`)}
          >
            Branch here
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
