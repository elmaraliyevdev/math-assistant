import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useSimulationActivity } from '@/features/collaboration/hooks/use-collaboration'
import { formatDate } from '@/lib/utils'

interface ActivityTimelineProps {
  simulationId: string
}

export function ActivityTimeline({ simulationId }: ActivityTimelineProps) {
  const activity = useSimulationActivity(simulationId)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Activity history</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {activity.isLoading && (
          <p className="text-sm text-muted-foreground">Loading activity…</p>
        )}
        {!activity.isLoading && activity.data?.items.length === 0 && (
          <p className="text-sm text-muted-foreground">No activity yet.</p>
        )}
        <ul className="space-y-3">
          {activity.data?.items.map((entry) => (
            <li key={entry.id} className="rounded-md border p-3">
              <p className="font-medium">{entry.action.replaceAll('_', ' ')}</p>
              <p className="text-xs text-muted-foreground">
                {formatDate(entry.createdAt)}
              </p>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}
