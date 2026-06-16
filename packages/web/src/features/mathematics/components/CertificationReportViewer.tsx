import { useMemo } from 'react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { formatPercent } from '@/lib/utils'
import type { CertificationReportResponse } from '@/types/api'

interface CertificationReportViewerProps {
  report: CertificationReportResponse
  onDownload: (format: 'json' | 'pdf') => void
  downloading?: boolean
}

export function CertificationReportViewer({
  report,
  onDownload,
  downloading = false,
}: CertificationReportViewerProps) {
  const previewLines = useMemo(
    () => buildPreviewLines(report),
    [report],
  )

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Certification Report Preview</CardTitle>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={downloading}
              onClick={() => onDownload('json')}
            >
              Download JSON
            </Button>
            <Button
              size="sm"
              disabled={downloading}
              onClick={() => onDownload('pdf')}
            >
              Download PDF
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <pre className="max-h-[420px] overflow-auto rounded-md bg-muted/40 p-4 text-xs leading-relaxed">
            {previewLines.join('\n')}
          </pre>
        </CardContent>
      </Card>
    </div>
  )
}

function buildPreviewLines(report: CertificationReportResponse): string[] {
  const lines = [
    'Certification Mathematics Report',
    `Game: ${report.gameTitle}`,
    `Game Version: ${report.gameVersionId}`,
    '',
    'RTP Summary',
    `  Target RTP: ${report.targetRtp ?? 'n/a'}%`,
    `  Theoretical RTP: ${formatPercent(report.theoreticalRtp.totalRtp)}`,
    `  Simulated RTP: ${report.simulatedRtp ?? 'n/a'}%`,
    `  RTP Variance: ${report.rtpVariance ?? 'n/a'}`,
    '',
    'Feature Probabilities',
  ]

  for (const feature of report.featureProbabilities) {
    lines.push(
      `  ${feature.trigger}: ${(feature.probability * 100).toFixed(4)}%` +
        (feature.oneInX ? ` (1 in ${feature.oneInX})` : ''),
    )
  }

  lines.push(
    '',
    'Exposure',
    `  Max Win: ${report.exposure.maxWinMinorUnits}`,
    `  Cap Scope: ${report.exposure.capScope}`,
  )

  if (report.discrepancy) {
    lines.push('', 'Discrepancy', `  ${report.discrepancy.summary}`)
  }

  if (report.recommendations.length > 0) {
    lines.push('', 'Recommendations')
    for (const rec of report.recommendations) {
      lines.push(`  - ${rec.action}`)
    }
  }

  return lines
}
