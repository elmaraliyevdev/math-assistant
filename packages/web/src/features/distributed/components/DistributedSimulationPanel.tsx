import { Button } from '@/components/ui/button'
import {
  ShardProgressTable,
} from '@/features/distributed/components/ShardProgressTable'
import {
  useRetryFailedShards,
  useSimulationShards,
} from '@/features/distributed/hooks/use-distributed'

interface DistributedSimulationPanelProps {
  simulationId: string
  distributedExecution: boolean
  enabled?: boolean
}

export function DistributedSimulationPanel({
  simulationId,
  distributedExecution,
  enabled = true,
}: DistributedSimulationPanelProps) {
  const shards = useSimulationShards(
    simulationId,
    enabled && distributedExecution,
  )
  const retry = useRetryFailedShards(simulationId)

  if (!distributedExecution) {
    return null
  }

  if (shards.isLoading || !shards.data) {
    return (
      <p className="text-sm text-muted-foreground">Loading shard progress…</p>
    )
  }

  return (
    <div className="space-y-4">
      <ShardProgressTable
        shards={shards.data.items}
        totalShards={shards.data.totalShards}
        completedShards={shards.data.completedShards}
        progressPercentage={shards.data.progressPercentage}
      />
      {shards.data.failedShards > 0 && (
        <Button
          variant="outline"
          onClick={() => retry.mutate()}
          disabled={retry.isPending}
        >
          Retry failed shards ({shards.data.failedShards})
        </Button>
      )}
    </div>
  )
}
