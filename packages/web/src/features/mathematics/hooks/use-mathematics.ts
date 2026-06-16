import { useMutation } from '@tanstack/react-query'

import {
  mathematicsApi,
  type CalibrateRequest,
  type CertificationReportRequest,
  type MathematicsRequest,
} from '@/features/mathematics/api/mathematics-api'

export function useTheoreticalAnalysis() {
  return useMutation({
    mutationFn: (body: MathematicsRequest) => mathematicsApi.theoretical(body),
  })
}

export function useCalibrateMathematics() {
  return useMutation({
    mutationFn: (body: CalibrateRequest) => mathematicsApi.calibrate(body),
  })
}

export function useCertificationReport() {
  return useMutation({
    mutationFn: (body: CertificationReportRequest) =>
      mathematicsApi.certificationReport(body),
  })
}

export function useDownloadCertificationReport() {
  return useMutation({
    mutationFn: ({
      body,
      format,
    }: {
      body: CertificationReportRequest
      format: 'json' | 'pdf'
    }) => mathematicsApi.downloadCertificationReport(body, format),
  })
}
