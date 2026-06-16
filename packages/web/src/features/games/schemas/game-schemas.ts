import { z } from 'zod'

export const gameFormSchema = z.object({
  name: z.string().min(1, 'Name is required').max(255),
  description: z.string().max(2000).optional(),
})

export type GameFormValues = z.infer<typeof gameFormSchema>

export const DEFAULT_ENGINE_VERSION = 'runtime-core@1.8.0'

export const versionUploadSchema = z.object({
  engineVersion: z.string().min(1, 'Engine version is required'),
  canonicalJsonText: z
    .string()
    .min(2, 'Canonical JSON is required')
    .refine((value) => {
      try {
        JSON.parse(value)
        return true
      } catch {
        return false
      }
    }, 'Invalid JSON syntax'),
})

export type VersionUploadFormValues = z.infer<typeof versionUploadSchema>

export function parseCanonicalJson(text: string): Record<string, unknown> {
  return JSON.parse(text) as Record<string, unknown>
}
