import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useSimulationLimits } from '@/features/simulations/hooks/use-simulation-limits'

interface SimulationLimitsNoticeProps {
  spinCount: number
}

export function SimulationLimitsNotice({ spinCount }: SimulationLimitsNoticeProps) {
  const { limits, guidance, isLoading } = useSimulationLimits(spinCount)

  if (isLoading || !limits) {
    return null
  }

  return (
    <Card className="border-dashed">
      <CardHeader className="pb-2">
        <CardTitle className="text-base">Deployment limits</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 text-sm text-muted-foreground">
        <p>
          Mode: <span className="font-medium text-foreground">{limits.deploymentMode}</span>
        </p>
        <p>
          Max spins per simulation:{' '}
          <span className="font-medium text-foreground">
            {limits.maxSimulationSpinCount.toLocaleString()}
          </span>
        </p>
        {limits.maxActiveSimulations !== null && (
          <p>
            Active simulations:{' '}
            <span className="font-medium text-foreground">
              {limits.activeSimulationCount} / {limits.maxActiveSimulations}
            </span>
          </p>
        )}
        {guidance && (
          <p className="rounded-md bg-destructive/10 p-2 text-destructive">{guidance}</p>
        )}
      </CardContent>
    </Card>
  )
}
