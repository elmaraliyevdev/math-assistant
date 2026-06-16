import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useSimulationQueue } from '@/features/distributed/hooks/use-distributed'

export function SimulationQueueWidget() {
  const queue = useSimulationQueue()

  return (
    <Card>
      <CardHeader>
        <CardTitle>Simulation queue</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-2 gap-3 text-sm">
        <div>
          <p className="text-muted-foreground">Pending</p>
          <p className="text-2xl font-bold">{queue.data?.pendingTasks ?? 0}</p>
        </div>
        <div>
          <p className="text-muted-foreground">Running</p>
          <p className="text-2xl font-bold">{queue.data?.runningTasks ?? 0}</p>
        </div>
        <div>
          <p className="text-muted-foreground">Completed</p>
          <p className="text-2xl font-bold">{queue.data?.completedTasks ?? 0}</p>
        </div>
        <div>
          <p className="text-muted-foreground">Failed</p>
          <p className="text-2xl font-bold">{queue.data?.failedTasks ?? 0}</p>
        </div>
      </CardContent>
    </Card>
  )
}
