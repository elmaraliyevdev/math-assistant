import { moveSymbol, swapSymbols, reelsToStrips, stripsToReels } from '@/features/reel-studio/generator/placement'
import type { OptimizationProposal } from '@/features/reel-studio/optimizer/optimizer-types'
import type { StudioReelStrip } from '@/features/reel-studio/types'
import type { ProposalApplicator } from '@/features/reel-studio/optimizer/interfaces'

function cloneStrips(reels: StudioReelStrip[]): StudioReelStrip[] {
  return reels.map((reel, reelIndex) => ({
    reelIndex,
    symbols: [...reel.symbols],
    weights: reel.weights ? [...reel.weights] : undefined,
  }))
}

function applyMove(
  reels: string[][],
  fromReel: number,
  fromPos: number,
  toReel: number,
  toPos: number,
): string[][] {
  return moveSymbol(reels, fromReel, fromPos, toReel, toPos)
}

function applySwap(
  reels: string[][],
  reelA: number,
  posA: number,
  reelB: number,
  posB: number,
): string[][] {
  return swapSymbols(reels, reelA, posA, reelB, posB)
}

export class DefaultProposalApplicator implements ProposalApplicator {
  applyProposal(reels: StudioReelStrip[], proposal: OptimizationProposal): StudioReelStrip[] {
    return this.previewProposal(reels, proposal)
  }

  previewProposal(reels: StudioReelStrip[], proposal: OptimizationProposal): StudioReelStrip[] {
    let matrix = stripsToReels(reels)
    if (proposal.before.length === 1 && proposal.after.length === 1) {
      const from = proposal.before[0]!
      const to = proposal.after[0]!
      matrix = applyMove(matrix, from.reelIndex, from.symbolIndex, to.reelIndex, to.symbolIndex)
    } else if (proposal.before.length === 2 && proposal.after.length === 2) {
      const a = proposal.before[0]!
      const b = proposal.before[1]!
      matrix = applySwap(matrix, a.reelIndex, a.symbolIndex, b.reelIndex, b.symbolIndex)
    }
    return reelsToStrips(matrix)
  }
}

export function applyProposalToReels(
  reels: StudioReelStrip[],
  proposal: OptimizationProposal,
): StudioReelStrip[] {
  return new DefaultProposalApplicator().applyProposal(cloneStrips(reels), proposal)
}

export function previewProposalOnReels(
  reels: StudioReelStrip[],
  proposal: OptimizationProposal,
): StudioReelStrip[] {
  return new DefaultProposalApplicator().previewProposal(cloneStrips(reels), proposal)
}
