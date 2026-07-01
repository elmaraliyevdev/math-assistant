/** Deterministic seeded PRNG (Mulberry32). */

export function createSeededRng(seed: number): () => number {
  let state = seed >>> 0
  return () => {
    state += 0x6d2b79f5
    let t = state
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

export function shuffleWithSeed<T>(items: T[], seed: number): T[] {
  const rng = createSeededRng(seed)
  const next = [...items]
  for (let index = next.length - 1; index > 0; index -= 1) {
    const swapIndex = Math.floor(rng() * (index + 1))
    const temp = next[index]!
    next[index] = next[swapIndex]!
    next[swapIndex] = temp
  }
  return next
}

export function seededInt(seed: number, min: number, max: number): number {
  const rng = createSeededRng(seed)
  return Math.floor(rng() * (max - min + 1)) + min
}
