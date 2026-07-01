'use client'

import { Badge, statusBadgeVariant } from '@/components/ui/badge'
import { formatNumber } from '@/lib/utils'

import { useDemoSimulation } from '../hooks/use-demo-simulation'

/** Marketing composition: huge progress + converging RTP / volatility. */
export function SimulationPreview() {
  const simulation = useDemoSimulation()
  const isComplete = simulation.status === 'completed'

  return (
    <div className="demo-preview-shell">
      <div className="demo-preview-feature demo-simulation-preview">
        <div className="demo-simulation-preview__header">
          <Badge variant={statusBadgeVariant(isComplete ? 'completed' : 'running')}>
            {isComplete ? 'Complete' : 'Running'}
          </Badge>
          <p className="demo-simulation-preview__percent tabular-nums">
            {simulation.progress.toFixed(1)}%
          </p>
        </div>

        <div className="demo-simulation-preview__track" role="progressbar" aria-valuenow={simulation.progress}>
          <div
            className="demo-simulation-preview__fill"
            style={{ width: `${Math.min(simulation.progress, 100)}%` }}
          />
        </div>

        <p className="demo-simulation-preview__spins tabular-nums">
          {formatNumber(simulation.spinCount)}
          <span className="text-muted-foreground">
            {' '}
            / {formatNumber(simulation.targetSpins)} spins
          </span>
        </p>

        <dl className="demo-simulation-preview__metrics">
          <div>
            <dt>Observed RTP</dt>
            <dd className="tabular-nums">{simulation.rtpDisplay}</dd>
          </div>
          <div>
            <dt>Volatility σ</dt>
            <dd className="tabular-nums">{simulation.volatilityDisplay}</dd>
          </div>
        </dl>
      </div>
    </div>
  )
}
