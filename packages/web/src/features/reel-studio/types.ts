export type SymbolType = 'regular' | 'wild' | 'scatter' | 'bonus'

export interface StudioSymbol {
  id: string
  displayName?: string
  type: SymbolType
}

export interface StudioReelStrip {
  reelIndex: number
  symbols: string[]
  weights?: number[]
}

export interface StudioReelSet {
  id: string
  reels: StudioReelStrip[]
}

export interface ReelStudioDocument {
  symbols: Record<string, StudioSymbol>
  reelSets: Record<string, StudioReelSet>
  activeReelSetId: string
  originalCanonicalJson: Record<string, unknown>
  engineVersion: string
}

export interface ReelSymbolStats {
  symbolId: string
  count: number
  percentage: number
}

export interface ReelStats {
  reelIndex: number
  length: number
  symbols: ReelSymbolStats[]
  duplicateSymbolIds: string[]
}

export interface ReelSetStats {
  reelSetId: string
  reels: ReelStats[]
  totals: {
    totalSymbols: number
    symbolCounts: ReelSymbolStats[]
    duplicateSymbolIds: string[]
  }
}
