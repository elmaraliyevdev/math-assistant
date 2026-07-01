import type { ReelStudioDocument, StudioReelSet, StudioReelStrip } from '@/features/reel-studio/types'

function cloneReelSet(reelSet: StudioReelSet): StudioReelSet {
  return {
    id: reelSet.id,
    reels: reelSet.reels.map((reel) => ({
      reelIndex: reel.reelIndex,
      symbols: [...reel.symbols],
      weights: reel.weights ? [...reel.weights] : undefined,
    })),
  }
}

function syncWeights(
  symbols: string[],
  weights: number[] | undefined,
  operation: (weights: number[]) => number[] | undefined,
): number[] | undefined {
  if (!weights || weights.length === 0) {
    return undefined
  }
  const next = operation([...weights])
  if (!next || next.length !== symbols.length) {
    return undefined
  }
  return next
}

function moveWeight(weights: number[], from: number, to: number): number[] {
  const next = [...weights]
  const [value] = next.splice(from, 1)
  if (value === undefined) {
    return weights
  }
  next.splice(to, 0, value)
  return next
}

function getActiveReelSet(document: ReelStudioDocument): StudioReelSet {
  const reelSet = document.reelSets[document.activeReelSetId]
  if (!reelSet) {
    throw new Error(`Reel set not found: ${document.activeReelSetId}`)
  }
  return reelSet
}

function updateActiveReelSet(
  document: ReelStudioDocument,
  updater: (reelSet: StudioReelSet) => StudioReelSet,
): ReelStudioDocument {
  const current = getActiveReelSet(document)
  return {
    ...document,
    reelSets: {
      ...document.reelSets,
      [document.activeReelSetId]: updater(cloneReelSet(current)),
    },
  }
}

function normalizeReelIndexes(reelSet: StudioReelSet): StudioReelSet {
  return {
    ...reelSet,
    reels: reelSet.reels.map((reel, index) => ({
      ...reel,
      reelIndex: index,
    })),
  }
}

export function setActiveReelSetId(
  document: ReelStudioDocument,
  reelSetId: string,
): ReelStudioDocument {
  if (!document.reelSets[reelSetId]) {
    return document
  }
  return { ...document, activeReelSetId: reelSetId }
}

export function replaceActiveReelSet(
  document: ReelStudioDocument,
  reels: StudioReelStrip[],
): ReelStudioDocument {
  return updateActiveReelSet(document, (reelSet) =>
    normalizeReelIndexes({
      ...reelSet,
      reels: reels.map((reel, index) => ({
        reelIndex: index,
        symbols: [...reel.symbols],
        weights: reel.weights ? [...reel.weights] : undefined,
      })),
    }),
  )
}

export function moveSymbolWithinReel(
  document: ReelStudioDocument,
  reelIndex: number,
  fromIndex: number,
  toIndex: number,
): ReelStudioDocument {
  return updateActiveReelSet(document, (reelSet) => {
    const reels = reelSet.reels.map((reel) => {
      if (reel.reelIndex !== reelIndex) {
        return reel
      }
      const symbols = [...reel.symbols]
      const [moved] = symbols.splice(fromIndex, 1)
      if (!moved) {
        return reel
      }
      symbols.splice(toIndex, 0, moved)
      const weights = syncWeights(symbols, reel.weights, (current) =>
        moveWeight(current, fromIndex, toIndex),
      )
      return { ...reel, symbols, weights }
    })
    return { ...reelSet, reels }
  })
}

export function moveSymbolBetweenReels(
  document: ReelStudioDocument,
  fromReelIndex: number,
  fromSymbolIndex: number,
  toReelIndex: number,
  toSymbolIndex: number,
): ReelStudioDocument {
  return updateActiveReelSet(document, (reelSet) => {
    const reels = reelSet.reels.map((reel) => ({
      ...reel,
      symbols: [...reel.symbols],
    }))
    const fromReel = reels.find((reel) => reel.reelIndex === fromReelIndex)
    const toReel = reels.find((reel) => reel.reelIndex === toReelIndex)
    if (!fromReel || !toReel) {
      return reelSet
    }
    const [symbol] = fromReel.symbols.splice(fromSymbolIndex, 1)
    if (!symbol) {
      return reelSet
    }
    const fromWeight = fromReel.weights?.[fromSymbolIndex]
    if (fromReel.weights) {
      fromReel.weights.splice(fromSymbolIndex, 1)
      if (fromReel.weights.length === 0) {
        fromReel.weights = undefined
      }
    }
    const insertAt =
      fromReelIndex === toReelIndex && fromSymbolIndex < toSymbolIndex
        ? toSymbolIndex - 1
        : toSymbolIndex
    toReel.symbols.splice(insertAt, 0, symbol)
    if (fromWeight !== undefined && toReel.weights) {
      toReel.weights.splice(insertAt, 0, fromWeight)
    } else if (fromWeight !== undefined) {
      toReel.weights = undefined
    }
    return normalizeReelIndexes({ ...reelSet, reels })
  })
}

export function addSymbolToReel(
  document: ReelStudioDocument,
  reelIndex: number,
  symbolId: string,
  position?: number,
): ReelStudioDocument {
  return updateActiveReelSet(document, (reelSet) => {
    const reels = reelSet.reels.map((reel) => {
      if (reel.reelIndex !== reelIndex) {
        return reel
      }
      const symbols = [...reel.symbols]
      const index = position ?? symbols.length
      symbols.splice(index, 0, symbolId)
      const weights = reel.weights ? undefined : reel.weights
      return { ...reel, symbols, weights }
    })
    return { ...reelSet, reels }
  })
}

export function removeSymbolFromReel(
  document: ReelStudioDocument,
  reelIndex: number,
  symbolIndex: number,
): ReelStudioDocument {
  return updateActiveReelSet(document, (reelSet) => {
    const reels = reelSet.reels.map((reel) => {
      if (reel.reelIndex !== reelIndex) {
        return reel
      }
      const symbols = reel.symbols.filter((_, index) => index !== symbolIndex)
      const weights = syncWeights(symbols, reel.weights, (current) => {
        const next = [...current]
        next.splice(symbolIndex, 1)
        return next
      })
      return { ...reel, symbols, weights }
    })
    return { ...reelSet, reels }
  })
}

export function duplicateSymbolOnReel(
  document: ReelStudioDocument,
  reelIndex: number,
  symbolIndex: number,
): ReelStudioDocument {
  return updateActiveReelSet(document, (reelSet) => {
    const reels = reelSet.reels.map((reel) => {
      if (reel.reelIndex !== reelIndex) {
        return reel
      }
      const symbol = reel.symbols[symbolIndex]
      if (!symbol) {
        return reel
      }
      const symbols = [...reel.symbols]
      symbols.splice(symbolIndex + 1, 0, symbol)
      const weights = syncWeights(symbols, reel.weights, (current) => {
        const next = [...current]
        const weight = current[symbolIndex]
        if (weight === undefined) {
          return current
        }
        next.splice(symbolIndex + 1, 0, weight)
        return next
      })
      return { ...reel, symbols, weights }
    })
    return { ...reelSet, reels }
  })
}

export function parseSlotId(
  id: string,
): { reelIndex: number; symbolIndex: number } | null {
  const match = /^slot-(\d+)-(\d+)$/.exec(id)
  if (!match) {
    return null
  }
  return {
    reelIndex: Number(match[1]),
    symbolIndex: Number(match[2]),
  }
}

export function slotId(reelIndex: number, symbolIndex: number): string {
  return `slot-${reelIndex}-${symbolIndex}`
}

export function paletteId(symbolId: string): string {
  return `palette-${symbolId}`
}

export function parsePaletteId(id: string): string | null {
  if (!id.startsWith('palette-')) {
    return null
  }
  return id.slice('palette-'.length)
}

export function reelContainerId(reelIndex: number): string {
  return `reel-container-${reelIndex}`
}

export function parseReelContainerId(id: string): number | null {
  const match = /^reel-container-(\d+)$/.exec(id)
  return match ? Number(match[1]) : null
}
