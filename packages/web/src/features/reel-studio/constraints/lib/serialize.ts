import type { ConstraintDocument, ConstraintPreset } from '@/features/reel-studio/constraints/types'

export function serializeConstraintDocument(document: ConstraintDocument): string {
  return JSON.stringify(document, null, 2)
}

export function parseConstraintDocument(raw: string): ConstraintDocument {
  const parsed = JSON.parse(raw) as ConstraintDocument
  if (parsed.version !== 1) {
    throw new Error('Unsupported constraint document version')
  }
  return parsed
}

export function exportPreset(preset: ConstraintPreset): string {
  return JSON.stringify(preset, null, 2)
}

export function importPreset(raw: string): ConstraintPreset {
  const parsed = JSON.parse(raw) as ConstraintPreset
  if (!parsed.id || !parsed.document) {
    throw new Error('Invalid preset JSON')
  }
  return { ...parsed, builtIn: false }
}

export function duplicatePreset(preset: ConstraintPreset, newId: string, newName: string): ConstraintPreset {
  return {
    ...structuredClone(preset),
    id: newId,
    name: newName,
    builtIn: false,
  }
}
