import type { OptimizationProposal, ProposalPriority } from '@/features/reel-studio/optimizer/optimizer-types'

const PRIORITY_WEIGHT: Record<ProposalPriority, number> = {
  critical: 400,
  high: 300,
  medium: 200,
  low: 100,
}

export function rankProposals(proposals: OptimizationProposal[]): OptimizationProposal[] {
  return [...proposals].sort((left, right) => {
    const leftScore =
      PRIORITY_WEIGHT[left.priority] +
      left.healthGain * 10 +
      left.violationsFixed * 15 -
      left.complexity * 3 -
      (left.estimatedRisk === 'high' ? 20 : left.estimatedRisk === 'medium' ? 8 : 0)
    const rightScore =
      PRIORITY_WEIGHT[right.priority] +
      right.healthGain * 10 +
      right.violationsFixed * 15 -
      right.complexity * 3 -
      (right.estimatedRisk === 'high' ? 20 : right.estimatedRisk === 'medium' ? 8 : 0)
    if (rightScore !== leftScore) {
      return rightScore - leftScore
    }
    return left.id.localeCompare(right.id)
  })
}

export function topProposals(
  proposals: OptimizationProposal[],
  count: number,
): OptimizationProposal[] {
  return rankProposals(proposals).slice(0, Math.max(0, count))
}
