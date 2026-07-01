import { useState } from 'react'

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion'
import { cn } from '@/lib/utils'
import type { SimulationIntelligenceReport, SimulationResults } from '@/types/api'

const SEVERITY_ICON: Record<string, string> = {
  red: '🔴',
  yellow: '🟡',
  green: '🟢',
}

function buildFindings(
  results: SimulationResults,
): Array<{ id: string; severity: string; title: string; detail: string }> {
  const findings: Array<{ id: string; severity: string; title: string; detail: string }> = []

  if (results.rtpValidation && !results.rtpValidation.withinTolerance) {
    const diff = results.rtpValidation.difference
    findings.push({
      id: 'rtp',
      severity: Math.abs(diff) > 0.02 ? 'red' : 'yellow',
      title: `RTP ${Math.abs(diff * 100).toFixed(1)}% ${diff < 0 ? 'below' : 'above'} target`,
      detail: `Target ${(results.rtpValidation.targetRtp * 100).toFixed(2)}%, observed ${(results.rtpValidation.actualRtp * 100).toFixed(2)}%.`,
    })
  }

  for (const item of results.featureValidation) {
    if (item.status === 'pass') continue
    findings.push({
      id: `feature-${item.feature}`,
      severity: item.status === 'fail' ? 'red' : 'yellow',
      title: `${item.feature} frequency ${item.status === 'fail' ? 'off target' : 'drifting'}`,
      detail: `Observed ${(item.observedFrequency * 100).toFixed(2)}% vs expected ${(item.expectedFrequency * 100).toFixed(2)}%.`,
    })
  }

  if (results.simulationIntelligence) {
    for (const item of results.simulationIntelligence.designVsReality) {
      if (item.status === 'green') {
        findings.push({
          id: item.metricId,
          severity: 'green',
          title: `${item.label} matches design`,
          detail: `Target ${item.target}, observed ${item.observed}.`,
        })
        continue
      }
      findings.push({
        id: item.metricId,
        severity: item.status === 'red' ? 'red' : 'yellow',
        title: `${item.label} diverges from design`,
        detail: `Target ${item.target}, observed ${item.observed}. Confidence ${item.confidence.score}%.`,
      })
    }
  }

  for (const rec of results.recommendations) {
    findings.push({
      id: rec.title,
      severity: rec.severity === 'critical' ? 'red' : rec.severity === 'warning' ? 'yellow' : 'green',
      title: rec.title,
      detail: rec.description,
    })
  }

  const unique = new Map<string, (typeof findings)[number]>()
  for (const finding of findings) {
    if (!unique.has(finding.id)) unique.set(finding.id, finding)
  }

  const ordered = [...unique.values()]
  ordered.sort((a, b) => severityRank(a.severity) - severityRank(b.severity))
  return ordered.slice(0, 8)
}

function severityRank(severity: string) {
  if (severity === 'red') return 0
  if (severity === 'yellow') return 1
  return 2
}

export function SimulationTopInsights({
  results,
  intelligence,
}: {
  results: SimulationResults
  intelligence?: SimulationIntelligenceReport | null
}) {
  const findings = buildFindings({ ...results, simulationIntelligence: intelligence })
  const [expanded, setExpanded] = useState<string | null>(findings[0]?.id ?? null)

  if (findings.length === 0) return null

  return (
    <section className="space-y-3">
      <div>
        <h2 className="text-lg font-medium">Top findings</h2>
        <p className="text-sm text-muted-foreground">
          What matters most from this simulation run.
        </p>
      </div>
      <Accordion
        type="single"
        collapsible
        value={expanded ?? undefined}
        onValueChange={setExpanded}
        className="rounded-xl border border-border/40 bg-card/30 px-4"
      >
        {findings.map((finding) => (
          <AccordionItem key={finding.id} value={finding.id} className="border-border/40">
            <AccordionTrigger className="py-3 hover:no-underline">
              <span className="flex items-center gap-2 text-left text-sm">
                <span aria-hidden>{SEVERITY_ICON[finding.severity] ?? '•'}</span>
                <span className="font-medium">{finding.title}</span>
              </span>
            </AccordionTrigger>
            <AccordionContent className={cn('pb-3 text-sm text-muted-foreground')}>
              {finding.detail}
            </AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    </section>
  )
}
