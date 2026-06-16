import { api } from '@/services/api'
import type { EngineVersion } from '@/types/api'

export const engineService = {
  async getVersion(): Promise<EngineVersion> {
    const { data } = await api.get<EngineVersion>('/engine/version')
    return data
  },
}
