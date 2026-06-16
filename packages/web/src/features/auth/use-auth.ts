import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'

import { authService } from '@/services/auth'
import { isOnboardingCompleted } from '@/features/onboarding/storage'
import { useAuthStore } from '@/stores/auth-store'
import { useOrganizationStore } from '@/stores/organization-store'

export const authKeys = {
  me: ['auth', 'me'] as const,
}

export function useMe(enabled = true) {
  return useQuery({
    queryKey: authKeys.me,
    queryFn: () => authService.me(),
    enabled: enabled && useAuthStore.getState().isAuthenticated(),
  })
}

export function useLogin() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: authService.login,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: authKeys.me })
      await navigate({ to: '/dashboard' })
    },
  })
}

export function useRegister() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: authService.register,
    onSuccess: async (data) => {
      useOrganizationStore.getState().setCurrentOrganizationId(data.organizationId)
      await queryClient.invalidateQueries({ queryKey: authKeys.me })
      await navigate({
        to: isOnboardingCompleted() ? '/dashboard' : '/onboarding',
      })
    },
  })
}

export function useLogout() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: authService.logout,
    onSuccess: async () => {
      useOrganizationStore.getState().clear()
      queryClient.clear()
      await navigate({ to: '/login' })
    },
  })
}

export function useBootstrapSession() {
  return useMutation({
    mutationFn: async () => {
      const existing = useAuthStore.getState().accessToken
      if (existing) {
        return authService.me()
      }
      const refreshed = await authService.refresh()
      if (!refreshed) {
        throw new Error('No session')
      }
      return authService.me()
    },
  })
}
