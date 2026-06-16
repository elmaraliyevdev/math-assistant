import { ChevronDown, ChevronRight } from 'lucide-react'
import { useState, type ReactNode } from 'react'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { extractMathConfigSnapshot } from '@/features/simulations/utils/workbench'
import { formatNumber } from '@/lib/utils'

interface MathConfigurationSnapshotProps {
  canonicalJson: Record<string, unknown>
}

export function MathConfigurationSnapshot({
  canonicalJson,
}: MathConfigurationSnapshotProps) {
  const [expanded, setExpanded] = useState(false)
  const snapshot = extractMathConfigSnapshot(canonicalJson)

  return (
    <Card>
      <CardHeader>
        <button
          type="button"
          className="flex w-full items-center gap-2 text-left"
          onClick={() => setExpanded((value) => !value)}
          aria-expanded={expanded}
        >
          {expanded ? (
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          ) : (
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
          )}
          <CardTitle>Math configuration snapshot</CardTitle>
        </button>
      </CardHeader>
      {expanded && (
        <CardContent className="space-y-6 text-sm">
          <Section title="RTP target">
            {snapshot.rtpTarget ? (
              <p>
                {snapshot.rtpTarget.percent.toFixed(2)}%
                {snapshot.rtpTarget.tolerance != null
                  ? ` (±${snapshot.rtpTarget.tolerance.toFixed(2)}%)`
                  : ''}
              </p>
            ) : (
              <p className="text-muted-foreground">Not configured</p>
            )}
          </Section>

          <Section title="Scatter triggers">
            {snapshot.scatterTriggers.length === 0 ? (
              <p className="text-muted-foreground">None configured</p>
            ) : (
              <TriggerTable triggers={snapshot.scatterTriggers} />
            )}
          </Section>

          <Section title="Hold & Win / bonus triggers">
            {snapshot.bonusTriggers.length === 0 ? (
              <p className="text-muted-foreground">None configured</p>
            ) : (
              <TriggerTable triggers={snapshot.bonusTriggers} />
            )}
          </Section>

          <Section title="Jackpot tiers">
            {Object.keys(snapshot.jackpotTiers).length === 0 ? (
              <p className="text-muted-foreground">None configured</p>
            ) : (
              <ul className="space-y-1">
                {Object.entries(snapshot.jackpotTiers).map(([tier, multiplier]) => (
                  <li key={tier}>
                    {tier}: {formatNumber(multiplier)}x bet
                  </li>
                ))}
              </ul>
            )}
          </Section>

          <Section title="Exposure cap">
            <p>
              Max win:{' '}
              {snapshot.exposureCap.maxWinMinorUnits != null
                ? `${formatNumber(snapshot.exposureCap.maxWinMinorUnits)} minor units`
                : '—'}
            </p>
            <p>
              Max multiplier:{' '}
              {snapshot.exposureCap.maxWinMultiplier != null
                ? `${snapshot.exposureCap.maxWinMultiplier}x`
                : '—'}
            </p>
          </Section>

          <Section title="Paytable summary">
            {snapshot.paytableSummary.length === 0 ? (
              <p className="text-muted-foreground">No line pays configured</p>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="pb-2 pr-4 font-medium">Symbol</th>
                    <th className="pb-2 pr-4 font-medium">Count</th>
                    <th className="pb-2 font-medium">Multiplier</th>
                  </tr>
                </thead>
                <tbody>
                  {snapshot.paytableSummary.map((row) => (
                    <tr key={`${row.symbolId}-${row.count}`} className="border-b last:border-0">
                      <td className="py-2 pr-4">{row.symbolId}</td>
                      <td className="py-2 pr-4">{row.count}</td>
                      <td className="py-2">{row.multiplier}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </Section>
        </CardContent>
      )}
    </Card>
  )
}

function Section({
  title,
  children,
}: {
  title: string
  children: ReactNode
}) {
  return (
    <div>
      <h4 className="mb-2 font-medium">{title}</h4>
      {children}
    </div>
  )
}

function TriggerTable({
  triggers,
}: {
  triggers: Array<{
    state: string
    symbolId: string
    minCount: number
    emitTrigger: string
  }>
}) {
  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="border-b text-left text-muted-foreground">
          <th className="pb-2 pr-4 font-medium">State</th>
          <th className="pb-2 pr-4 font-medium">Symbol</th>
          <th className="pb-2 pr-4 font-medium">Min count</th>
          <th className="pb-2 font-medium">Feature</th>
        </tr>
      </thead>
      <tbody>
        {triggers.map((trigger) => (
          <tr
            key={`${trigger.state}-${trigger.symbolId}-${trigger.minCount}`}
            className="border-b last:border-0"
          >
            <td className="py-2 pr-4">{trigger.state}</td>
            <td className="py-2 pr-4">{trigger.symbolId}</td>
            <td className="py-2 pr-4">{trigger.minCount}</td>
            <td className="py-2">{trigger.emitTrigger}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
