import { api } from '@/services/api'
import type {
  CalibrateResponse,
  CertificationReportResponse,
  TheoreticalAnalysisResponse,
} from '@/types/api'

export interface MathematicsRequest {
  gameVersionId: string
  reelSetId?: string
  totalBetMinorUnits?: number
  simulationId?: string
}

export interface CalibrateRequest extends MathematicsRequest {
  simulatedRtp?: number
  tolerance?: number
}

export interface CertificationReportRequest extends MathematicsRequest {
  simulatedRtp?: number
  rtpVariance?: number
  tolerance?: number
  format?: 'json' | 'pdf'
}

export const mathematicsApi = {
  async theoretical(body: MathematicsRequest): Promise<TheoreticalAnalysisResponse> {
    const { data } = await api.post<TheoreticalAnalysisResponse>(
      '/mathematics/theoretical',
      body,
    )
    return data
  },

  async calibrate(body: CalibrateRequest): Promise<CalibrateResponse> {
    const { data } = await api.post<CalibrateResponse>(
      '/mathematics/calibrate',
      body,
    )
    return data
  },

  async certificationReport(
    body: CertificationReportRequest,
  ): Promise<CertificationReportResponse> {
    const { data } = await api.post<CertificationReportResponse>(
      '/mathematics/certification-report',
      body,
    )
    return data
  },

  async downloadCertificationReport(
    body: CertificationReportRequest,
    format: 'json' | 'pdf',
  ): Promise<Blob> {
    const { data } = await api.post<Blob>(
      '/mathematics/certification-report',
      { ...body, format },
      { responseType: 'blob' },
    )
    return data
  },
}
