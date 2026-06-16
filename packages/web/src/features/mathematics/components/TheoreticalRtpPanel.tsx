import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { formatPercent } from '@/lib/utils'
import type { TheoreticalAnalysisResponse } from '@/types/api'

interface TheoreticalRtpPanelProps {
  data: TheoreticalAnalysisResponse
}

export function TheoreticalRtpPanel({ data }: TheoreticalRtpPanelProps) {
  const { rtp, featureProbabilities } = data

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Theoretical RTP</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 sm:grid-cols-2">
          <Metric label="Total / Base RTP" value={formatPercent(rtp.totalRtp)} />
          <Metric label="Line RTP" value={formatPercent(rtp.lineRtp)} />
          <Metric label="Scatter RTP" value={formatPercent(rtp.scatterRtp)} />
          <Metric label="Outcomes enumerated" value={rtp.outcomeCount.toLocaleString()} />
          <Metric label="Reel set" value={rtp.reelSetId} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Feature Trigger Probabilities</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {featureProbabilities.length === 0 ? (
            <p className="text-sm text-muted-foreground">No feature triggers configured.</p>
          ) : (
            featureProbabilities.map((feature) => (
              <div
                key={feature.trigger}
                className="flex items-center justify-between rounded-md border px-3 py-2 text-sm"
              >
                <span className="font-medium">{feature.trigger}</span>
                <span className="text-muted-foreground">
                  {(feature.probability * 100).toFixed(4)}%
                  {feature.oneInX ? ` · 1 in ${feature.oneInX}` : ''}
                </span>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs uppercase tracking-wide text-muted-foreground">{label}</p>
      <p className="text-lg font-semibold">{value}</p>
    </div>
  )
}
