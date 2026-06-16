import { Badge, statusBadgeVariant } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import type { SimulationShard } from '@/features/distributed/api/distributed-api'

interface ShardProgressTableProps {
  shards: SimulationShard[]
  totalShards: number
  completedShards: number
  progressPercentage: number
}

export function ShardProgressTable({
  shards,
  totalShards,
  completedShards,
  progressPercentage,
}: ShardProgressTableProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Distributed shards</CardTitle>
        <p className="text-sm text-muted-foreground">
          {completedShards} / {totalShards} shards complete ({progressPercentage}%)
        </p>
        <Progress value={progressPercentage} className="h-2" />
      </CardHeader>
      <CardContent className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-muted-foreground">
              <th className="py-2">Shard</th>
              <th>Spins</th>
              <th>Status</th>
              <th>Worker</th>
            </tr>
          </thead>
          <tbody>
            {shards.map((shard) => (
              <tr key={shard.id} className="border-b">
                <td className="py-2 font-medium">Shard {shard.shardIndex}</td>
                <td>{shard.spinCount}</td>
                <td>
                  <Badge variant={statusBadgeVariant(shard.status)}>
                    {shard.status}
                  </Badge>
                </td>
                <td className="font-mono text-xs">{shard.workerId ?? '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardContent>
    </Card>
  )
}
