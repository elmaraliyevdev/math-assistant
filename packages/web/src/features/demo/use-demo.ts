import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { demoService } from '@/services/demo'

export const demoKeys = {
  overview: ['demo', 'overview'] as const,
}

export function useDemoOverview(enabled = true) {
  return useQuery({
    queryKey: demoKeys.overview,
    queryFn: () => demoService.getOverview(),
    enabled,
    retry: false,
    staleTime: 5 * 60_000,
  })
}

export function useDuplicateDemo() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => demoService.duplicateToWorkspace(),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: demoKeys.overview })
    },
  })
}
