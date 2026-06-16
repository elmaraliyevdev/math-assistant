import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { notificationsApi } from '@/services/notifications'

export const notificationKeys = {
  all: ['notifications'] as const,
  list: (params: Record<string, unknown>) =>
    ['notifications', 'list', params] as const,
}

export function useNotifications(params: {
  page?: number
  pageSize?: number
  type?: string
  unreadOnly?: boolean
} = {}) {
  return useQuery({
    queryKey: notificationKeys.list(params),
    queryFn: () => notificationsApi.list(params),
    refetchInterval: 30_000,
  })
}

export function useMarkNotificationRead() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: notificationsApi.markRead,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: notificationKeys.all })
    },
  })
}

export function useMarkAllNotificationsRead() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => notificationsApi.markAllRead(),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: notificationKeys.all })
    },
  })
}
