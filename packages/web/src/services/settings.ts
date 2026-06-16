import { api } from '@/services/api'
import type { User } from '@/types/api'

export interface UserPreferences {
  theme: string
  notifySimulationCompleted: boolean
  notifySimulationFailed: boolean
  notifyValidationFailed: boolean
  notifyOrganizationInvitation: boolean
}

export const settingsApi = {
  getPreferences() {
    return api
      .get<UserPreferences>('/users/me/preferences')
      .then((r) => r.data)
  },
  updatePreferences(body: Partial<UserPreferences>) {
    return api
      .patch<UserPreferences>('/users/me/preferences', body)
      .then((r) => r.data)
  },
  updateProfile(body: { fullName?: string }) {
    return api.patch<User>('/users/me/profile', body).then((r) => r.data)
  },
  changePassword(body: { currentPassword: string; newPassword: string }) {
    return api.post('/users/me/change-password', body)
  },
}
