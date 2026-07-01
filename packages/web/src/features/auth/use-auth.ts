import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'

import { identifyUser, resetAnalytics, trackEvent } from '@/lib/analytics'
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
    onSuccess: async (data, variables) => {
      identifyUser(data.accessToken ? 'authenticated' : 'user')
      await queryClient.invalidateQueries({ queryKey: authKeys.me })
      await navigate({ to: '/dashboard' })
      void variables
    },
  })
}

export function useRegister() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: authService.register,
    onSuccess: async (data) => {
      trackEvent('signup')
      identifyUser(data.user.id, { email: data.user.email })
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
      resetAnalytics()
      useOrganizationStore.getState().clear()
      queryClient.clear()
      await navigate({ to: '/login' })
    },
  })
}

export function useForgotPassword() {
  return useMutation({
    mutationFn: authService.forgotPassword,
  })
}

export function useResetPassword() {
  return useMutation({
    mutationFn: authService.resetPassword,
  })
}

export function useVerifyEmail() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: authService.verifyEmail,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: authKeys.me })
    },
  })
}

export function useResendVerification() {
  return useMutation({
    mutationFn: authService.resendVerification,
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
