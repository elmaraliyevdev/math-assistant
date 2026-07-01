import { useMemo, useState } from 'react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { useCreateSimulationNote } from '@/features/simulations/hooks/use-simulations'
import {
  buildReviewPacketNote,
  listTuningDecisions,
  upsertTuningDecision,
  type TuningDecisionStatus,
} from '@/features/workbench/tuning-decisions'
import type { SimulationIntelligenceReport, SimulationResults } from '@/types/api'
import { cn } from '@/lib/utils'

type RecommendationItem = SimulationResults['recommendations'][number] & {
  key: string
  status: TuningDecisionStatus
  note: string
}

const severityTone: Record<string, string> = {
  critical: 'bg-destructive/10 text-destructive',
  warning: 'bg-amber-500/10 text-amber-800 dark:text-amber-300',
  info: 'bg-muted text-muted-foreground',
}

export function SimulationRecommendationsTimeline({
  simulationId,
  recommendations,
  intelligence,
}: {
  simulationId: string
  recommendations: SimulationResults['recommendations']
  intelligence?: SimulationIntelligenceReport | null
}) {
  const createNote = useCreateSimulationNote(simulationId)
  const [decisions, setDecisions] = useState(() => listTuningDecisions(simulationId))
  const [expanded, setExpanded] = useState<string | null>(null)

  const merged = useMemo(() => {
    const base: RecommendationItem[] = recommendations.map((item) => {
      const key = item.title
      const existing = decisions.find((decision) => decision.recommendationKey === key)
      return {
        ...item,
        key,
        status: existing?.status ?? 'pending',
        note: existing?.note ?? '',
      }
    })

    if (intelligence?.recommendations.length) {
      for (const item of intelligence.recommendations) {
        if (base.some((entry) => entry.title === item.title)) continue
        const existing = decisions.find((decision) => decision.recommendationKey === item.id)
        base.push({
          severity: item.confidence.score >= 90 ? 'critical' : 'warning',
          title: item.title,
          description: item.recommendation,
          key: item.id,
          status: existing?.status ?? 'pending',
          note: existing?.note ?? '',
        })
      }
    }

    return base
  }, [decisions, intelligence?.recommendations, recommendations])

  function updateDecision(
    recommendationKey: string,
    title: string,
    description: string,
    status: TuningDecisionStatus,
  ) {
    const next = upsertTuningDecision(simulationId, {
      recommendationKey,
      title,
      description,
      status,
      note: '',
    })
    setDecisions(next)
  }

  if (merged.length === 0) return null

  return (
    <section className="space-y-3">
      <div>
        <h2 className="text-lg font-medium">Recommendations</h2>
        <p className="text-sm text-muted-foreground">
          Prioritized actions with accept / reject workflow.
        </p>
      </div>
      <div className="space-y-3">
        {merged.map((item) => (
          <article
            key={item.key}
            className="rounded-xl border border-border/40 bg-card/30 p-4"
          >
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="space-y-2">
                <div className="flex flex-wrap items-center gap-2">
                  <Badge
                    variant="secondary"
                    className={cn('border-0 capitalize', severityTone[item.severity] ?? '')}
                  >
                    {item.severity}
                  </Badge>
                  {item.status !== 'pending' && (
                    <Badge variant="outline" className="capitalize">
                      {item.status}
                    </Badge>
                  )}
                </div>
                <h3 className="font-medium">{item.title}</h3>
              </div>
              <div className="flex flex-wrap gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() =>
                    updateDecision(item.key, item.title, item.description, 'accepted')
                  }
                >
                  Accept
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() =>
                    updateDecision(item.key, item.title, item.description, 'rejected')
                  }
                >
                  Reject
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() =>
                    setExpanded((current) => (current === item.key ? null : item.key))
                  }
                >
                  {expanded === item.key ? 'Hide details' : 'Open details'}
                </Button>
              </div>
            </div>
            {expanded === item.key ? (
              <p className="mt-3 text-sm text-muted-foreground">{item.description}</p>
            ) : null}
          </article>
        ))}
      </div>
      <Button
        variant="outline"
        size="sm"
        disabled={createNote.isPending}
        onClick={() => createNote.mutate(buildReviewPacketNote(decisions))}
      >
        Save review packet to notes
      </Button>
    </section>
  )
}
