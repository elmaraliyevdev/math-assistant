import type { ReactNode } from 'react'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { GlossaryTerm } from '@/components/glossary-term'
import type { GlossaryTermKey } from '@/lib/glossary'
import { formatNumber, formatPercent } from '@/lib/utils'

interface MetricItem {
  label: string
  value: string
  glossaryTerm?: GlossaryTermKey
}

interface MetricsCardsProps {
  title: ReactNode
  metrics: MetricItem[]
}

function MetricLabel({ label, glossaryTerm }: Pick<MetricItem, 'label' | 'glossaryTerm'>) {
  if (glossaryTerm) {
    return <GlossaryTerm term={glossaryTerm}>{label}</GlossaryTerm>
  }
  return <>{label}</>
}

export function MetricsCards({ title, metrics }: MetricsCardsProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold">{title}</h3>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {metrics.map((metric) => (
          <Card key={metric.label}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                <MetricLabel
                  label={metric.label}
                  glossaryTerm={metric.glossaryTerm}
                />
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold tracking-tight">{metric.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

export function formatMetricPercent(value: number): string {
  return formatPercent(value)
}

export function formatMetricNumber(value: number): string {
  return formatNumber(value)
}
