import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { settingsApi, type UserPreferences } from '@/services/settings'
import { useThemeStore } from '@/stores/theme-store'
import { toast } from '@/lib/toast'

export const settingsKeys = {
  preferences: ['settings', 'preferences'] as const,
}

export function useUserPreferences() {
  return useQuery({
    queryKey: settingsKeys.preferences,
    queryFn: settingsApi.getPreferences,
  })
}

export function useUpdatePreferences() {
  const queryClient = useQueryClient()
  const setTheme = useThemeStore((s) => s.setTheme)

  return useMutation({
    mutationFn: (body: Partial<UserPreferences>) =>
      settingsApi.updatePreferences(body),
    onSuccess: async (data) => {
      if (data.theme === 'light' || data.theme === 'dark') {
        setTheme(data.theme)
      }
      await queryClient.invalidateQueries({ queryKey: settingsKeys.preferences })
      toast.success('Preferences saved')
    },
  })
}

export function useUpdateProfile() {
  return useMutation({
    mutationFn: settingsApi.updateProfile,
    onSuccess: () => toast.success('Profile updated'),
  })
}

export function useChangePassword() {
  return useMutation({
    mutationFn: settingsApi.changePassword,
    onSuccess: () => toast.success('Password changed'),
  })
}
