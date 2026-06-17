import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { CertificationReadinessPanel } from '@/features/mathematics/components/CertificationReadinessPanel'
import { RtpGaugeChart } from '@/features/mathematics/components/RtpGaugeChart'
import type { CalibrateResponse } from '@/types/api'

interface CalibrationDashboardProps {
  data: CalibrateResponse
}

export function CalibrationDashboard({ data }: CalibrationDashboardProps) {
  const { calibration, discrepancy, recommendations } = data

  const statusVariant = (status: string) => {
    if (status === 'certification_blocked') return 'danger'
    if (status === 'critical' || status === 'major') return 'danger'
    if (status === 'moderate' || status === 'warning') return 'warning'
    return 'secondary'
  }

  return (
    <div className="space-y-4">
      <CertificationReadinessPanel readiness={data.certificationReadiness} />

      <Card>
        <CardHeader>
          <CardTitle>RTP Calibration</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-6 md:grid-cols-3">
          <RtpGaugeChart label="Target RTP" value={calibration.targetRtp} />
          <RtpGaugeChart label="Theoretical RTP" value={calibration.theoreticalRtp} />
          <RtpGaugeChart label="Simulated RTP" value={calibration.simulatedRtp} />
        </CardContent>
        {(calibration.discrepancySeverity || calibration.certificationStatus) && (
          <CardContent className="flex flex-wrap gap-2 border-t pt-4">
            {calibration.discrepancySeverity && (
              <Badge variant={statusVariant(calibration.discrepancySeverity)}>
                Gap severity: {calibration.discrepancySeverity}
              </Badge>
            )}
            {calibration.certificationStatus && (
              <Badge variant={statusVariant(calibration.certificationStatus)}>
                {calibration.certificationStatus.replaceAll('_', ' ')}
              </Badge>
            )}
            {calibration.rtpGapPp != null && (
              <span className="text-sm text-muted-foreground">
                RTP gap: {calibration.rtpGapPp.toFixed(2)} pp
              </span>
            )}
          </CardContent>
        )}
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Discrepancy Analysis</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-muted-foreground">{discrepancy.summary}</p>
          {discrepancy.items.map((item) => (
            <div
              key={item.metric}
              className="flex flex-wrap items-center justify-between gap-2 rounded-md border px-3 py-2 text-sm"
            >
              <span className="font-medium">{item.metric}</span>
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">Δ {item.delta}</span>
                <Badge variant={statusVariant(item.status)}>
                  {item.status.replaceAll('_', ' ')}
                </Badge>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Recommendations</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {recommendations.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No calibration recommendations for the current configuration.
            </p>
          ) : (
            recommendations.map((rec) => (
              <div key={`${rec.category}-${rec.action}`} className="rounded-md border p-3">
                <div className="mb-1 flex flex-wrap items-center gap-2">
                  <Badge variant={rec.severity === 'warning' ? 'warning' : rec.severity === 'critical' ? 'danger' : 'secondary'}>
                    {rec.severity}
                  </Badge>
                  <Badge variant="outline">{rec.discrepancySeverity}</Badge>
                  <span className="text-xs uppercase text-muted-foreground">
                    {rec.category}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    Est. {rec.estimatedRtpContributionPp.toFixed(2)} pp
                  </span>
                </div>
                <p className="font-medium">{rec.action}</p>
                <p className="mt-1 text-sm text-muted-foreground">
                  {rec.expectedRtpImpact}
                </p>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  )
}
