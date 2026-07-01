import type { StudioReelStrip } from '@/features/reel-studio/types'

export function reelsToStrips(reels: string[][]): StudioReelStrip[] {
  return reels.map((symbols, reelIndex) => ({
    reelIndex,
    symbols: [...symbols],
  }))
}

export function stripsToReels(strips: StudioReelStrip[]): string[][] {
  return strips.map((strip) => [...strip.symbols])
}

export function placePoolOnReels(pool: string[], reelLengths: number[]): string[][] {
  const reels: string[][] = reelLengths.map(() => [])
  let index = 0
  for (let reelIndex = 0; reelIndex < reelLengths.length; reelIndex += 1) {
    const length = reelLengths[reelIndex] ?? 0
    for (let position = 0; position < length; position += 1) {
      reels[reelIndex]!.push(pool[index] ?? pool[pool.length - 1] ?? 'A')
      index += 1
    }
  }
  return reels
}

export function swapSymbols(
  reels: string[][],
  reelA: number,
  posA: number,
  reelB: number,
  posB: number,
): string[][] {
  const next = reels.map((reel) => [...reel])
  const a = next[reelA]?.[posA]
  const b = next[reelB]?.[posB]
  if (a === undefined || b === undefined) {
    return reels
  }
  next[reelA]![posA] = b
  next[reelB]![posB] = a
  return next
}

export function moveSymbol(
  reels: string[][],
  fromReel: number,
  fromPos: number,
  toReel: number,
  toPos: number,
): string[][] {
  const next = reels.map((reel) => [...reel])
  const symbol = next[fromReel]?.[fromPos]
  if (!symbol) {
    return reels
  }
  next[fromReel]!.splice(fromPos, 1)
  next[toReel]!.splice(toPos, 0, symbol)
  return next
}

export function rotateReel(reels: string[][], reelIndex: number, steps: number): string[][] {
  const next = reels.map((reel) => [...reel])
  const reel = next[reelIndex]
  if (!reel || reel.length === 0) {
    return reels
  }
  const offset = ((steps % reel.length) + reel.length) % reel.length
  next[reelIndex] = [...reel.slice(offset), ...reel.slice(0, offset)]
  return next
}
