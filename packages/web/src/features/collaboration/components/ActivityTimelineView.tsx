import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { SimulationActivity } from '@/features/collaboration/types'
import { formatDate } from '@/lib/utils'

export function ActivityTimelineView({
  items,
}: {
  items: SimulationActivity[]
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Activity history</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <ul className="space-y-3">
          {items.map((entry) => (
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
