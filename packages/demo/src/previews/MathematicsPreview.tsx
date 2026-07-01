'use client'

import { useMemo } from 'react'

import { Badge } from '@/components/ui/badge'

import { demoCalibrateResponse } from '../data/mathematics'
import { useMetricCounter } from '../hooks/use-metric-counter'
import { MarketingHeroGauge } from './MarketingHeroGauge'

/** Marketing composition: hero gauge + target / difference / PASS. */
export function MathematicsPreview() {
  const { calibration } = demoCalibrateResponse
  const target = calibration.targetRtp ?? 96
  const simulated = calibration.simulatedRtp ?? 95.96

  const gauge = useMetricCounter({
    from: target - 1.2,
    to: simulated,
    intervalMs: 45,
    step: 0.06,
    precision: 2,
    autoStart: true,
  })

  const difference = useMemo(() => simulated - target, [simulated, target])
  const showPass = gauge.value >= simulated - 0.05

  return (
    <div className="demo-preview-shell">
      <div className="demo-preview-feature demo-math-preview">
        <div className="demo-math-preview__gauge">
          <MarketingHeroGauge label="Simulated RTP" value={gauge.value} />
        </div>
        <div className="demo-math-preview__stats">
          <div className="demo-math-preview__stat">
            <span className="demo-math-preview__stat-label">Target RTP</span>
            <span className="demo-math-preview__stat-value tabular-nums">
              {target.toFixed(2)}%
            </span>
          </div>
          <div className="demo-math-preview__stat">
            <span className="demo-math-preview__stat-label">Difference</span>
            <span className="demo-math-preview__stat-value tabular-nums">
              {difference >= 0 ? '+' : ''}
              {difference.toFixed(2)} pp
            </span>
          </div>
          <Badge
            variant={calibration.withinTolerance ? 'success' : 'warning'}
            className={showPass ? 'demo-animate-pass' : 'opacity-40'}
          >
            {calibration.withinTolerance ? 'PASS' : 'REVIEW'}
          </Badge>
        </div>
      </div>
    </div>
  )
}
