import { normalizeSymbolType } from '@/features/reel-studio/lib/symbol-colors'
import type {
  ReelStudioDocument,
  StudioReelSet,
  StudioReelStrip,
  StudioSymbol,
} from '@/features/reel-studio/types'

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function parseSymbols(raw: unknown): Record<string, StudioSymbol> {
  if (!isRecord(raw)) {
    return {}
  }
  const symbols: Record<string, StudioSymbol> = {}
  for (const [key, entry] of Object.entries(raw)) {
    if (!isRecord(entry)) {
      continue
    }
    const id = typeof entry.id === 'string' ? entry.id : key
    symbols[id] = {
      id,
      displayName:
        typeof entry.displayName === 'string' ? entry.displayName : undefined,
      type: normalizeSymbolType(entry.type),
    }
  }
  return symbols
}

function parseReelStrip(raw: unknown, reelIndex: number): StudioReelStrip | null {
  if (!isRecord(raw)) {
    return null
  }
  const symbols = Array.isArray(raw.symbols)
    ? raw.symbols.filter((item): item is string => typeof item === 'string')
    : []
  const weights = Array.isArray(raw.weights)
    ? raw.weights.filter((item): item is number => typeof item === 'number')
    : undefined
  const index =
    typeof raw.reelIndex === 'number' ? raw.reelIndex : reelIndex
  return {
    reelIndex: index,
    symbols: [...symbols],
    weights: weights && weights.length > 0 ? [...weights] : undefined,
  }
}

function parseReelSet(raw: unknown, fallbackId: string): StudioReelSet | null {
  if (!isRecord(raw)) {
    return null
  }
  const id = typeof raw.id === 'string' ? raw.id : fallbackId
  const reelsRaw = Array.isArray(raw.reels) ? raw.reels : []
  const reels = reelsRaw
    .map((reel, index) => parseReelStrip(reel, index))
    .filter((reel): reel is StudioReelStrip => reel !== null)
    .sort((a, b) => a.reelIndex - b.reelIndex)
  return { id, reels }
}

function parseReelSets(raw: unknown): Record<string, StudioReelSet> {
  if (!isRecord(raw)) {
    return {}
  }
  const reelSets: Record<string, StudioReelSet> = {}
  for (const [key, value] of Object.entries(raw)) {
    const parsed = parseReelSet(value, key)
    if (parsed) {
      reelSets[key] = parsed
    }
  }
  return reelSets
}

function resolveDefaultReelSetId(
  canonicalJson: Record<string, unknown>,
  reelSets: Record<string, StudioReelSet>,
): string {
  const gameConfig = canonicalJson.gameConfig
  if (isRecord(gameConfig) && typeof gameConfig.defaultReelSetId === 'string') {
    if (reelSets[gameConfig.defaultReelSetId]) {
      return gameConfig.defaultReelSetId
    }
  }
  const keys = Object.keys(reelSets)
  return keys[0] ?? 'base_game'
}

export function parseCanonicalJson(
  canonicalJson: Record<string, unknown>,
  engineVersion: string,
): ReelStudioDocument {
  const reelSets = parseReelSets(canonicalJson.reelSets)
  return {
    symbols: parseSymbols(canonicalJson.symbols),
    reelSets,
    activeReelSetId: resolveDefaultReelSetId(canonicalJson, reelSets),
    originalCanonicalJson: structuredClone(canonicalJson),
    engineVersion,
  }
}
