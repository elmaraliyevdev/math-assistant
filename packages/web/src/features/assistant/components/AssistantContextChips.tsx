import { Badge } from '@/components/ui/badge'
import type { AssistantContextState } from '@/features/assistant/types'
import { formatPercent } from '@/lib/utils'

const MODE_LABELS: Record<AssistantContextState['mode'], string> = {
  simulation: 'Simulation analysis',
  compare: 'Comparison',
  'game-version': 'Game design',
}

export function AssistantContextChips({
  context,
  gameName,
  versionNumber,
  healthScore,
  targetRtp,
}: {
  context: AssistantContextState
  gameName?: string
  versionNumber?: number | null
  healthScore?: number | null
  targetRtp?: number | null
}) {
  return (
    <div className="flex flex-wrap gap-2 border-b border-border/40 px-4 py-3">
      <Chip label="Mode" value={MODE_LABELS[context.mode]} />
      {gameName ? <Chip label="Game" value={gameName} /> : null}
      {versionNumber != null ? <Chip label="Version" value={`v${versionNumber}`} /> : null}
      {context.simulationId ? (
        <Chip label="Simulation" value={context.simulationId.slice(0, 8)} />
      ) : null}
      {healthScore != null ? <Chip label="Health" value={String(healthScore)} /> : null}
      {targetRtp != null ? (
        <Chip label="Target RTP" value={formatPercent(targetRtp)} />
      ) : null}
    </div>
  )
}

function Chip({ label, value }: { label: string; value: string }) {
  return (
    <Badge variant="secondary" className="gap-1.5 rounded-full border-0 bg-muted/60 font-normal">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-medium text-foreground">{value}</span>
    </Badge>
  )
}
