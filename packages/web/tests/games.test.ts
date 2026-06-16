import { describe, expect, it } from 'vitest'

import {
  gameFormSchema,
  parseCanonicalJson,
  versionUploadSchema,
} from '@/features/games/schemas/game-schemas'
import {
  getApiErrorCode,
  getValidationFindings,
  parseApiError,
} from '@/lib/api-error'
import type { ValidationFinding } from '@/features/games/types'

describe('gameFormSchema', () => {
  it('requires a name', () => {
    expect(gameFormSchema.safeParse({ name: '' }).success).toBe(false)
    expect(gameFormSchema.safeParse({ name: 'Lucky Stars' }).success).toBe(true)
  })
})

describe('versionUploadSchema', () => {
  it('rejects invalid JSON', () => {
    const result = versionUploadSchema.safeParse({
      engineVersion: 'runtime-core@1.8.0',
      canonicalJsonText: '{invalid',
    })
    expect(result.success).toBe(false)
  })

  it('accepts valid JSON text', () => {
    const result = versionUploadSchema.safeParse({
      engineVersion: 'runtime-core@1.8.0',
      canonicalJsonText: '{"schemaVersion":"1.0.0"}',
    })
    expect(result.success).toBe(true)
    expect(parseCanonicalJson('{"schemaVersion":"1.0.0"}')).toEqual({
      schemaVersion: '1.0.0',
    })
  })
})

describe('api error helpers', () => {
  it('parses validation failed errors', () => {
    const error = {
      isAxiosError: true,
      response: {
        data: {
          error: {
            code: 'VALIDATION_FAILED',
            message: 'failed',
            details: {
              findings: [
                {
                  code: 'CANONICAL_JSON_INVALID',
                  severity: 'error',
                  message: 'Invalid',
                  path: '/',
                },
              ] satisfies ValidationFinding[],
            },
          },
        },
      },
    }
    expect(getApiErrorCode(error)).toBe('VALIDATION_FAILED')
    expect(getValidationFindings(error)).toHaveLength(1)
    expect(parseApiError(error)?.code).toBe('VALIDATION_FAILED')
  })

  it('detects duplicate version errors', () => {
    const error = {
      isAxiosError: true,
      response: {
        data: {
          error: {
            code: 'DUPLICATE_GAME_VERSION',
            message: 'duplicate',
            details: { contentHash: 'abc', existingVersionId: 'v1' },
          },
        },
      },
    }
    expect(getApiErrorCode(error)).toBe('DUPLICATE_GAME_VERSION')
  })
})
