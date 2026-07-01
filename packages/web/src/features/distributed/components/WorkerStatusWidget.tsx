import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useWorkers } from '@/features/distributed/hooks/use-distributed'

export function WorkerStatusWidget() {
  const workers = useWorkers()

  if (workers.isError) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Worker status</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Simulations run in-process. Distributed workers are not configured.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Worker status</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {workers.isLoading && (
          <p className="text-sm text-muted-foreground">Loading workers…</p>
        )}
        <p className="text-sm">
          Active workers: {workers.data?.activeWorkers ?? 0}
        </p>
        {workers.data?.activeWorkers === 0 && !workers.isLoading && (
          <p className="text-sm text-muted-foreground">
            No Celery workers online. Simulations use the in-process queue.
          </p>
        )}
        {workers.data?.items.map((worker) => (
          <div key={worker.workerId} className="rounded-md border p-2 text-sm">
            <p className="font-mono">{worker.workerId}</p>
            <p className="text-muted-foreground">
              {worker.activeTasks} active · {worker.processedTasks} processed
            </p>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
