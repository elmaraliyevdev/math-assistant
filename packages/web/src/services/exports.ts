import { api } from '@/services/api'
import { downloadBlob } from '@/lib/export'

function filenameFromDisposition(
  disposition: string | undefined,
  fallback: string,
): string {
  const match = disposition?.match(/filename="(.+)"/)
  return match?.[1] ?? fallback
}

export const exportsApi = {
  async downloadSimulation(
    simulationId: string,
    format: 'json' | 'csv' | 'pdf',
  ) {
    const response = await api.get(`/simulations/${simulationId}/export`, {
      params: { format },
      responseType: 'blob',
    })
    const filename = filenameFromDisposition(
      response.headers['content-disposition'],
      `simulation-${simulationId}.${format}`,
    )
    downloadBlob(response.data, filename)
  },

  async downloadGameVersion(gameId: string, versionId: string) {
    const response = await api.get(
      `/games/${gameId}/versions/${versionId}/export`,
      { responseType: 'blob' },
    )
    const filename = filenameFromDisposition(
      response.headers['content-disposition'],
      `game-version-${versionId}.json`,
    )
    downloadBlob(response.data, filename)
  },

  async downloadComparison(simulationIds: string[], format: 'json' | 'pdf' = 'pdf') {
    const response = await api.get('/simulations/compare/export', {
      params: { ids: simulationIds.join(','), format },
      responseType: 'blob',
    })
    const filename = filenameFromDisposition(
      response.headers['content-disposition'],
      `simulation-comparison.${format}`,
    )
    downloadBlob(response.data, filename)
  },
}
