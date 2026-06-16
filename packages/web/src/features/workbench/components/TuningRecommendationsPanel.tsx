import { useMemo, useState } from 'react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { useCreateSimulationNote } from '@/features/simulations/hooks/use-simulations'
import {
  buildReviewPacketNote,
  listTuningDecisions,
  upsertTuningDecision,
  type TuningDecisionStatus,
} from '@/features/workbench/tuning-decisions'
import type { SimulationResults } from '@/types/api'

interface TuningRecommendationsPanelProps {
  simulationId: string
  recommendations: SimulationResults['recommendations']
}

const severityVariant: Record<string, 'default' | 'secondary' | 'danger' | 'outline' | 'warning'> = {
  info: 'secondary',
  warning: 'warning',
  critical: 'danger',
}

export function TuningRecommendationsPanel({
  simulationId,
  recommendations,
}: TuningRecommendationsPanelProps) {
  const createNote = useCreateSimulationNote(simulationId)
  const [decisions, setDecisions] = useState(() => listTuningDecisions(simulationId))

  const merged = useMemo(
    () =>
      recommendations.map((item) => {
        const key = item.title
        const existing = decisions.find((decision) => decision.recommendationKey === key)
        return {
          ...item,
          key,
          status: existing?.status ?? 'pending',
          note: existing?.note ?? '',
        }
      }),
    [decisions, recommendations],
  )

  function updateDecision(
    recommendationKey: string,
    title: string,
    description: string,
    status: TuningDecisionStatus,
    note: string,
  ) {
    const next = upsertTuningDecision(simulationId, {
      recommendationKey,
      title,
      description,
      status,
      note,
    })
    setDecisions(next)
  }

  if (recommendations.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Tuning recommendations</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            No tuning recommendations for this simulation.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between gap-4">
        <div>
          <CardTitle>Tuning recommendations</CardTitle>
          <p className="text-sm text-muted-foreground">
            Accept or reject suggestions and include them in review packets.
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          disabled={createNote.isPending || decisions.length === 0}
          onClick={() =>
            createNote.mutate(buildReviewPacketNote(decisions))
          }
        >
          Add review packet note
        </Button>
      </CardHeader>
      <CardContent className="space-y-4">
        {merged.map((item) => (
          <div key={item.key} className="rounded-lg border p-4">
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant={severityVariant[item.severity] ?? 'outline'}>
                {item.severity}
              </Badge>
              <p className="font-medium">{item.title}</p>
              <Badge variant={item.status === 'accepted' ? 'success' : item.status === 'rejected' ? 'danger' : 'secondary'}>
                {item.status}
              </Badge>
            </div>
            <p className="mt-2 text-sm text-muted-foreground">{item.description}</p>
            <div className="mt-3 flex flex-wrap gap-2">
              <Button
                size="sm"
                variant="outline"
                onClick={() =>
                  updateDecision(item.key, item.title, item.description, 'accepted', item.note)
                }
              >
                Accept
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() =>
                  updateDecision(item.key, item.title, item.description, 'rejected', item.note)
                }
              >
                Reject
              </Button>
            </div>
            <Input
              className="mt-3"
              placeholder="Add a note for this recommendation"
              value={item.note}
              onChange={(event) =>
                updateDecision(
                  item.key,
                  item.title,
                  item.description,
                  item.status as TuningDecisionStatus,
                  event.target.value,
                )
              }
            />
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
