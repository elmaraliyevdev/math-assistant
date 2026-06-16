import axios from 'axios'

import type { ValidationFinding } from '@/features/games/types'

export interface ApiErrorBody {
  error: {
    code: string
    message: string
    details?: Record<string, unknown>
  }
}

export function parseApiError(error: unknown): ApiErrorBody['error'] | null {
  if (!axios.isAxiosError(error)) {
    return null
  }
  const data = error.response?.data as ApiErrorBody | undefined
  return data?.error ?? null
}

export function getValidationFindings(error: unknown): ValidationFinding[] {
  const apiError = parseApiError(error)
  if (!apiError?.details?.findings) {
    return []
  }
  return apiError.details.findings as ValidationFinding[]
}

export function getApiErrorCode(error: unknown): string | null {
  return parseApiError(error)?.code ?? null
}
