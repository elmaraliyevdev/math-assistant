import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { SimulationIntelligenceReport } from '@/types/api'
import { formatNumber, formatPercent } from '@/lib/utils'

export function SimulationIntelligencePanel({
  intelligence,
}: {
  intelligence: SimulationIntelligenceReport
}) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Simulation intelligence overview</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <p>{intelligence.overview}</p>
          {intelligence.whyRtpDiffers.length > 0 ? (
            <div>
              <p className="font-medium">Why RTP differs</p>
              <ul className="mt-1 list-disc space-y-1 pl-5 text-muted-foreground">
                {intelligence.whyRtpDiffers.map((reason) => (
                  <li key={reason}>{reason}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Design vs reality</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {intelligence.designVsReality.map((item) => (
            <div
              key={item.metricId}
              className="flex items-center justify-between rounded-md border px-3 py-2 text-sm"
            >
              <div>
                <p className="font-medium">{item.label}</p>
                <p className="text-xs text-muted-foreground">
                  Target {item.target} · Observed {item.observed}
                </p>
              </div>
              <span
                className={
                  item.status === 'green'
                    ? 'text-emerald-600'
                    : item.status === 'yellow'
                      ? 'text-amber-600'
                      : 'text-red-600'
                }
              >
                {item.confidence.label} ({item.confidence.score}%)
              </span>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Evidence-backed recommendations</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {intelligence.recommendations.map((item) => (
            <div key={item.id} className="rounded-md border p-3 text-sm">
              <p className="font-medium">{item.title}</p>
              <p className="mt-1 text-muted-foreground">{item.recommendation}</p>
              <p className="mt-2 text-xs">
                Confidence {item.confidence.score}% · {item.expectedImprovement} · RTP influence:{' '}
                {item.potentialRtpInfluence}
              </p>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Contribution analysis</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {intelligence.contributionSlices.map((slice) => (
            <div key={slice.id} className="flex items-center justify-between text-sm">
              <span>{slice.label}</span>
              <span>{formatPercent(slice.rtpPercent / 100)}</span>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Symbol intelligence</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {intelligence.symbolProfiles.slice(0, 8).map((symbol) => (
            <div key={symbol.symbolId} className="rounded-md border p-3 text-sm">
              <div className="flex items-center justify-between">
                <p className="font-medium">{symbol.symbolId}</p>
                <span>{symbol.health}</span>
              </div>
              <p className="mt-1 text-xs text-muted-foreground">
                Observed {formatNumber(symbol.occurrences)} · Expected{' '}
                {formatNumber(symbol.expectedOccurrences)} · RTP contribution{' '}
                {formatPercent(symbol.rtpContributionPercent / 100)}
              </p>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Reel intelligence</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-2 sm:grid-cols-2">
          {intelligence.reelReports.map((reel) => (
            <div key={reel.reelIndex} className="rounded-md border p-3 text-sm">
              <p className="font-medium">
                Reel {reel.reelIndex + 1} · Rank {reel.rank}
              </p>
              <p className="text-xs text-muted-foreground">
                Length {reel.length} · Entropy {reel.entropy} · {reel.health}
              </p>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Simulation heatmaps</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {intelligence.heatmaps.map((heatmap) => (
            <div key={heatmap.id} className="rounded-md border p-3 text-sm">
              <p className="font-medium">{heatmap.label}</p>
              <p className="text-xs text-muted-foreground">Mode: {heatmap.mode}</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {Object.entries(heatmap.cells).map(([key, value]) => (
                  <span key={key} className="rounded bg-muted px-2 py-1 text-xs">
                    {key}: {value.toFixed(3)}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}
