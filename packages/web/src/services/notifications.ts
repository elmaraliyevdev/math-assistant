import { api } from '@/services/api'

export interface Notification {
  id: string
  type: string
  title: string
  message: string
  organizationId: string | null
  entityType: string | null
  entityId: string | null
  readAt: string | null
  createdAt: string
}

export interface NotificationListResponse {
  items: Notification[]
  total: number
  unreadCount: number
  page: number
  pageSize: number
}

export const notificationsApi = {
  list(params: {
    page?: number
    pageSize?: number
    type?: string
    unreadOnly?: boolean
  } = {}) {
    return api
      .get<NotificationListResponse>('/notifications', { params })
      .then((r) => r.data)
  },
  markRead(notificationId: string) {
    return api.post(`/notifications/${notificationId}/read`)
  },
  markAllRead() {
    return api.post('/notifications/read-all')
  },
}
