import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { SimulationResults } from '@/types/api'
import { formatPercent } from '@/lib/utils'

interface RtpValidationCardProps {
  validation: NonNullable<SimulationResults['rtpValidation']>
}

export function RtpValidationCard({ validation }: RtpValidationCardProps) {
  const status = validation.withinTolerance ? 'PASS' : 'FAIL'

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0">
        <CardTitle>RTP validation</CardTitle>
        <Badge variant={validation.withinTolerance ? 'success' : 'danger'}>
          {status}
        </Badge>
      </CardHeader>
      <CardContent className="grid gap-3 text-sm sm:grid-cols-2 lg:grid-cols-5">
        <Metric label="Target RTP" value={formatPercent(validation.targetRtp / 100, 2)} />
        <Metric label="Actual RTP" value={formatPercent(validation.actualRtp / 100, 2)} />
        <Metric
          label="Difference"
          value={`${validation.difference >= 0 ? '+' : ''}${validation.difference.toFixed(2)}%`}
        />
        <Metric label="Tolerance" value={`±${validation.tolerance.toFixed(2)}%`} />
        <Metric
          label="Within tolerance"
          value={validation.withinTolerance ? 'Yes' : 'No'}
        />
      </CardContent>
    </Card>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-muted-foreground">{label}</p>
      <p className="font-medium">{value}</p>
    </div>
  )
}
