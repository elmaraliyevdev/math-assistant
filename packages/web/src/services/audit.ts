import { api } from '@/services/api'

export interface AuditLog {
  id: string
  userId: string | null
  userEmail: string | null
  userName: string | null
  organizationId: string | null
  action: string
  entityType: string
  entityId: string | null
  metadata: Record<string, unknown> | null
  createdAt: string
}

export interface AuditLogListResponse {
  items: AuditLog[]
  total: number
  page: number
  pageSize: number
}

export const auditApi = {
  list(params: {
    page?: number
    pageSize?: number
    userId?: string
    action?: string
    dateFrom?: string
    dateTo?: string
  } = {}) {
    return api
      .get<AuditLogListResponse>('/audit', { params })
      .then((r) => r.data)
  },
}
