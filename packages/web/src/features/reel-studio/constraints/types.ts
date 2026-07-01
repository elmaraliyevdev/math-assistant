import type { StudioReelSet, StudioSymbol } from '@/features/reel-studio/types'

export type ConstraintType =
  | 'min_count'
  | 'max_count'
  | 'exact_count'
  | 'min_consecutive'
  | 'max_consecutive'
  | 'min_distance'
  | 'forbidden_adjacency'
  | 'allowed_adjacency'
  | 'reel_specific_count'

export type ConstraintTargetType = 'symbol' | 'group'

export type ValidationStatus = 'pass' | 'warning' | 'error'

export type ConstraintScope = 'global' | 'per_reel'

export interface SymbolGroup {
  id: string
  name: string
  symbolIds: string[]
}

export interface SymbolInventoryEntry {
  symbolId: string
  reelCounts: Record<string, number>
  totalTarget: number
}

export interface ConstraintRule {
  id: string
  type: ConstraintType
  enabled: boolean
  description: string
  targetType: ConstraintTargetType
  targetId: string
  secondaryTargetType?: ConstraintTargetType
  secondaryTargetId?: string
  value: number
  reelIndex?: number
  scope: ConstraintScope
  severity: 'warning' | 'error'
}

export interface ConstraintDocument {
  version: 1
  edgeWrapping: boolean
  groups: SymbolGroup[]
  inventory: Record<string, SymbolInventoryEntry>
  constraints: ConstraintRule[]
  activePresetId?: string
}

export interface AffectedPosition {
  reelIndex: number
  symbolIndex: number
}

export interface ValidationResultItem {
  constraintId: string
  constraintType: ConstraintType
  status: ValidationStatus
  message: string
  description: string
  expected: string
  actual: string
  affectedReels: number[]
  affectedPositions: AffectedPosition[]
  suggestedFix?: string
  category: string
}

export interface ConstraintValidationReport {
  results: ValidationResultItem[]
  summary: {
    pass: number
    warning: number
    error: number
    byCategory: Record<string, ValidationStatus>
  }
  violationsByPosition: Record<string, ValidationResultItem[]>
}

export interface ConstraintEngineInput {
  reelSet: StudioReelSet
  symbols: Record<string, StudioSymbol>
  constraintDocument: ConstraintDocument
}

export interface ConstraintPreset {
  id: string
  name: string
  description: string
  builtIn: boolean
  document: Omit<ConstraintDocument, 'activePresetId'>
}

export function positionKey(reelIndex: number, symbolIndex: number): string {
  return `${reelIndex}:${symbolIndex}`
}
