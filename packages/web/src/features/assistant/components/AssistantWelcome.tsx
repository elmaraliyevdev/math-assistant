import { Bot } from 'lucide-react'

import { MetricCard } from '@/components/design-system'
import { SUGGESTED_PROMPTS } from '@/features/assistant/lib/prompts'
import { formatPercent } from '@/lib/utils'

export function AssistantWelcome({
  simulationLoaded,
  healthScore,
  observedRtp,
  targetRtp,
  onPrompt,
}: {
  simulationLoaded?: boolean
  healthScore?: number | null
  observedRtp?: number | null
  targetRtp?: number | null
  onPrompt: (prompt: string) => void
}) {
  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col items-center px-4 py-10 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
        <Bot className="h-6 w-6" />
      </div>
      <h2 className="mt-4 text-2xl font-semibold tracking-tight">Mathematics Assistant</h2>
      <p className="mt-2 max-w-xl text-sm text-muted-foreground">
        I can analyze RTP, optimize volatility, explain simulations, recommend tuning, and
        compare game versions — grounded in your stored mathematics artifacts.
      </p>

      {simulationLoaded && (
        <div className="mt-8 grid w-full gap-3 sm:grid-cols-3">
          {healthScore != null ? (
            <MetricCard label="Health" value={healthScore} />
          ) : null}
          {observedRtp != null ? (
            <MetricCard label="Observed RTP" value={formatPercent(observedRtp)} />
          ) : null}
          {targetRtp != null ? (
            <MetricCard label="Target" value={formatPercent(targetRtp)} />
          ) : null}
        </div>
      )}

      <div className="mt-8 grid w-full gap-2 sm:grid-cols-2">
        {SUGGESTED_PROMPTS.map((prompt) => (
          <button
            key={prompt}
            type="button"
            onClick={() => onPrompt(prompt)}
            className="rounded-xl border border-border/40 bg-card/40 px-4 py-3 text-left text-sm transition-colors hover:border-primary/30 hover:bg-primary/5"
          >
            {prompt}
          </button>
        ))}
      </div>
    </div>
  )
}
