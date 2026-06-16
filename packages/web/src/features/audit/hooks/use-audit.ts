import { useQuery } from '@tanstack/react-query'

import { auditApi } from '@/services/audit'

export const auditKeys = {
  all: ['audit'] as const,
  list: (params: Record<string, unknown>) => ['audit', 'list', params] as const,
}

export function useAuditLogs(params: {
  page?: number
  pageSize?: number
  userId?: string
  action?: string
  dateFrom?: string
  dateTo?: string
} = {}) {
  return useQuery({
    queryKey: auditKeys.list(params),
    queryFn: () => auditApi.list(params),
  })
}
