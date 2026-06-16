import { useQuery } from '@tanstack/react-query'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { api } from '@/services/api'

function parseMetricLine(text: string, name: string): string | null {
  const line = text
    .split('\n')
    .find((entry) => entry.startsWith(name) && !entry.startsWith('#'))
  if (!line) return null
  const value = line.split(' ').pop()
  return value ?? null
}

export function MetricsOverview() {
  const metrics = useQuery({
    queryKey: ['metrics'],
    queryFn: async () => {
      const response = await api.get<string>('/metrics', {
        responseType: 'text',
        transformResponse: [(data) => data],
      })
      return response.data
    },
    refetchInterval: 60_000,
  })

  if (metrics.isLoading) {
    return <Skeleton className="h-32 w-full" />
  }

  const payload = metrics.data ?? ''
  const apiRequests = parseMetricLine(payload, 'api_requests_total')
  const simulations = parseMetricLine(payload, 'simulations_total')
  const queueSize = parseMetricLine(payload, 'simulation_worker_queue_size')

  return (
    <Card>
      <CardHeader>
        <CardTitle>System metrics</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-4 sm:grid-cols-3">
        <MetricItem label="API requests" value={apiRequests ?? '—'} />
        <MetricItem label="Simulations" value={simulations ?? '—'} />
        <MetricItem label="Worker queue" value={queueSize ?? '—'} />
      </CardContent>
    </Card>
  )
}

function MetricItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="font-mono text-lg font-semibold">{value}</p>
    </div>
  )
}
