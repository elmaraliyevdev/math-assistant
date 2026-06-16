import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import type { CalibrateResponse } from '@/types/api'
import { formatNumber, formatPercent } from '@/lib/utils'

interface CalibrationDashboardProps {
  data?: CalibrateResponse
  isLoading?: boolean
  error?: string | null
}

function formatMetricValue(metric: string, value: number | null | undefined): string {
  if (value == null) {
    return '—'
  }
  if (metric.toLowerCase().includes('rtp')) {
    return formatPercent(value > 1 ? value / 100 : value)
  }
  if (metric.toLowerCase().includes('frequency')) {
    return formatPercent(value)
  }
  return formatNumber(value)
}

export function CalibrationDashboard({
  data,
  isLoading,
  error,
}: CalibrationDashboardProps) {
  if (isLoading) {
    return <Skeleton className="h-48 w-full" />
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Calibration dashboard</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-destructive">{error}</p>
        </CardContent>
      </Card>
    )
  }

  if (!data) {
    return null
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Calibration dashboard</CardTitle>
        <p className="text-sm text-muted-foreground">
          Target, theoretical, and simulated metrics side by side.
        </p>
      </CardHeader>
      <CardContent className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-muted-foreground">
              <th className="pb-2 pr-4 font-medium">Metric</th>
              <th className="pb-2 pr-4 font-medium">Target</th>
              <th className="pb-2 pr-4 font-medium">Theoretical</th>
              <th className="pb-2 pr-4 font-medium">Simulated</th>
              <th className="pb-2 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {data.discrepancy.items.map((item) => (
              <tr key={item.metric} className="border-b last:border-0">
                <td className="py-3 pr-4 font-medium">{item.metric}</td>
                <td className="py-3 pr-4">{formatMetricValue(item.metric, item.target)}</td>
                <td className="py-3 pr-4">
                  {formatMetricValue(item.metric, item.theoretical)}
                </td>
                <td className="py-3 pr-4">
                  {formatMetricValue(item.metric, item.simulated)}
                </td>
                <td className="py-3">
                  <Badge variant={item.status === 'PASS' ? 'success' : 'danger'}>
                    {item.status}
                  </Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardContent>
    </Card>
  )
}
