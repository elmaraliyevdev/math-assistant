import { useQuery } from '@tanstack/react-query'

import { engineService } from '@/services/engine'

export const engineKeys = {
  version: ['engine', 'version'] as const,
}

export function useEngineVersion() {
  return useQuery({
    queryKey: engineKeys.version,
    queryFn: () => engineService.getVersion(),
    staleTime: 30_000,
  })
}
