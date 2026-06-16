import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { ShardProgressTable } from '@/features/distributed/components/ShardProgressTable'

describe('ShardProgressTable', () => {
  it('renders shard rows', () => {
    const client = new QueryClient()
    render(
      <QueryClientProvider client={client}>
        <ShardProgressTable
          shards={[
            {
              id: '1',
              simulationId: 'sim-1',
              shardIndex: 0,
              spinCount: 100,
              status: 'completed',
              workerId: 'worker-a',
              startedAt: null,
              completedAt: null,
              errorMessage: null,
            },
          ]}
          totalShards={4}
          completedShards={1}
          progressPercentage={25}
        />
      </QueryClientProvider>,
    )
    expect(screen.getByText('Shard 0')).toBeInTheDocument()
    expect(screen.getByText('completed')).toBeInTheDocument()
  })
})
