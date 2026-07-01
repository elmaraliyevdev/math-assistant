import { TrendingUp } from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useOptimizerStudio } from '@/features/reel-studio/optimizer/context/optimizer-context'

export function HealthEvolutionChart() {
  const { healthEvolution, iterationChain } = useOptimizerStudio()
  if (healthEvolution.length === 0) {
    return null
  }

  const max = Math.max(...healthEvolution, 100)
  const min = Math.min(...healthEvolution, 0)
  const range = Math.max(max - min, 1)

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm">
          <TrendingUp className="h-4 w-4" />
          Health evolution
        </CardTitle>
        <p className="text-xs text-muted-foreground">{healthEvolution.join(' → ')}</p>
      </CardHeader>
      <CardContent>
        <div className="flex h-24 items-end gap-1">
          {healthEvolution.map((health, index) => {
            const height = ((health - min) / range) * 100
            return (
              <div key={`${health}-${index}`} className="flex flex-1 flex-col items-center gap-1">
                <div
                  className="w-full rounded-t bg-primary"
                  style={{ height: `${Math.max(height, 8)}%` }}
                  title={`Iteration ${index + 1}: ${health}`}
                />
                <span className="text-[10px] text-muted-foreground">{health}</span>
              </div>
            )
          })}
        </div>
        {iterationChain[iterationChain.length - 1]?.healthReasons.length ? (
          <ul className="mt-3 space-y-1 text-xs text-muted-foreground">
            {iterationChain[iterationChain.length - 1]!.healthReasons.map((reason) => (
              <li key={reason}>• {reason}</li>
            ))}
          </ul>
        ) : null}
      </CardContent>
    </Card>
  )
}
