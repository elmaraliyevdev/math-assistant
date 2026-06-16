import { ChevronDown, ChevronRight } from 'lucide-react'
import { useState } from 'react'

import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { SimulationResults } from '@/types/api'

interface RecommendationsPanelProps {
  recommendations: SimulationResults['recommendations']
}

const severityVariant: Record<
  string,
  'default' | 'secondary' | 'danger' | 'outline' | 'warning'
> = {
  info: 'secondary',
  warning: 'warning',
  critical: 'danger',
}

export function RecommendationsPanel({ recommendations }: RecommendationsPanelProps) {
  if (recommendations.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recommendations</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            No tuning recommendations for this simulation. RTP and feature balance
            look within expected ranges.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recommendations</CardTitle>
        <p className="text-sm text-muted-foreground">
          Advisory suggestions based on simulation outcomes.
        </p>
      </CardHeader>
      <CardContent className="space-y-2">
        {recommendations.map((item) => (
          <RecommendationItem key={item.title} item={item} />
        ))}
      </CardContent>
    </Card>
  )
}

function RecommendationItem({
  item,
}: {
  item: SimulationResults['recommendations'][number]
}) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="rounded-lg border">
      <button
        type="button"
        className="flex w-full items-center gap-3 px-4 py-3 text-left hover:bg-muted/50"
        onClick={() => setExpanded((value) => !value)}
        aria-expanded={expanded}
      >
        {expanded ? (
          <ChevronDown className="h-4 w-4 shrink-0 text-muted-foreground" />
        ) : (
          <ChevronRight className="h-4 w-4 shrink-0 text-muted-foreground" />
        )}
        <Badge variant={severityVariant[item.severity] ?? 'outline'}>
          {item.severity}
        </Badge>
        <span className="font-medium">{item.title}</span>
      </button>
      {expanded && (
        <div className="border-t px-4 py-3 text-sm text-muted-foreground">
          {item.description}
        </div>
      )}
    </div>
  )
}
