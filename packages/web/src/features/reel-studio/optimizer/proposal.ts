import { runConstraintEngine } from '@/features/reel-studio/constraints/engine'
import type { ConstraintDocument } from '@/features/reel-studio/constraints/types'
import { computeDistribution } from '@/features/reel-studio/generator/distribution'
import { computeDesignHealth } from '@/features/reel-studio/generator/health'
import { moveSymbol, swapSymbols } from '@/features/reel-studio/generator/placement'
import { createSeededRng } from '@/features/reel-studio/generator/seed'
import { stripsToReels, reelsToStrips } from '@/features/reel-studio/generator/placement'
import type {
  OptimizationProposal,
  OptimizerInput,
  ProposalCategory,
  ProposalPriority,
} from '@/features/reel-studio/optimizer/optimizer-types'
import type { StudioReelSet, StudioSymbol } from '@/features/reel-studio/types'

function proposalId(seed: number, parts: string[]): string {
  let hash = seed >>> 0
  for (const part of parts) {
    for (let index = 0; index < part.length; index += 1) {
      hash = (hash * 31 + part.charCodeAt(index)) >>> 0
    }
  }
  return `proposal-${hash.toString(16)}`
}

function estimateHealthGain(
  before: StudioReelSet,
  after: StudioReelSet,
  symbols: Record<string, StudioSymbol>,
  constraintDocument: ConstraintDocument,
): number {
  const beforeHealth = computeDesignHealth(before, symbols, constraintDocument).overallScore
  const afterHealth = computeDesignHealth(after, symbols, constraintDocument).overallScore
  return afterHealth - beforeHealth
}

function buildMoveProposal(
  input: OptimizerInput,
  reelSet: StudioReelSet,
  fromReel: number,
  fromPos: number,
  toReel: number,
  toPos: number,
  meta: {
    title: string
    description: string
    reason: string
    category: ProposalCategory
    priority: ProposalPriority
    expectedImprovement: string[]
    confidence: number
    risk: OptimizationProposal['estimatedRisk']
    violationsFixed: number
  },
): OptimizationProposal | null {
  const reels = stripsToReels(reelSet.reels)
  const symbolId = reels[fromReel]?.[fromPos]
  if (!symbolId) {
    return null
  }
  const nextReels = moveSymbol(reels, fromReel, fromPos, toReel, toPos)
  const afterSet: StudioReelSet = { id: reelSet.id, reels: reelsToStrips(nextReels) }
  const healthGain = estimateHealthGain(reelSet, afterSet, input.symbols, input.constraintDocument)
  if (healthGain <= 0 && meta.priority !== 'critical') {
    return null
  }

  return {
    id: proposalId(input.seed, [meta.title, String(fromReel), String(fromPos), String(toReel), String(toPos)]),
    title: meta.title,
    description: meta.description,
    reason: meta.reason,
    priority: meta.priority,
    expectedImprovement: meta.expectedImprovement,
    affectedReels: [...new Set([fromReel, toReel])],
    affectedSymbols: [symbolId],
    before: [{ reelIndex: fromReel, symbolIndex: fromPos, symbolId }],
    after: [{ reelIndex: toReel, symbolIndex: toPos, symbolId }],
    healthGain: Math.max(healthGain, 1),
    confidence: meta.confidence,
    estimatedRisk: meta.risk,
    category: meta.category,
    violationsFixed: meta.violationsFixed,
    complexity: fromReel === toReel ? 1 : 2,
  }
}

function buildSwapProposal(
  input: OptimizerInput,
  reelSet: StudioReelSet,
  reelA: number,
  posA: number,
  reelB: number,
  posB: number,
  meta: {
    title: string
    description: string
    reason: string
    category: ProposalCategory
    priority: ProposalPriority
    expectedImprovement: string[]
    confidence: number
    risk: OptimizationProposal['estimatedRisk']
    violationsFixed: number
  },
): OptimizationProposal | null {
  const reels = stripsToReels(reelSet.reels)
  const symbolA = reels[reelA]?.[posA]
  const symbolB = reels[reelB]?.[posB]
  if (!symbolA || !symbolB) {
    return null
  }
  const nextReels = swapSymbols(reels, reelA, posA, reelB, posB)
  const afterSet: StudioReelSet = { id: reelSet.id, reels: reelsToStrips(nextReels) }
  const healthGain = estimateHealthGain(reelSet, afterSet, input.symbols, input.constraintDocument)
  if (healthGain <= 0 && meta.priority !== 'critical') {
    return null
  }

  return {
    id: proposalId(input.seed, [meta.title, String(reelA), String(posA), String(reelB), String(posB)]),
    title: meta.title,
    description: meta.description,
    reason: meta.reason,
    priority: meta.priority,
    expectedImprovement: meta.expectedImprovement,
    affectedReels: [...new Set([reelA, reelB])],
    affectedSymbols: [...new Set([symbolA, symbolB])],
    before: [
      { reelIndex: reelA, symbolIndex: posA, symbolId: symbolA },
      { reelIndex: reelB, symbolIndex: posB, symbolId: symbolB },
    ],
    after: [
      { reelIndex: reelA, symbolIndex: posA, symbolId: symbolB },
      { reelIndex: reelB, symbolIndex: posB, symbolId: symbolA },
    ],
    healthGain: Math.max(healthGain, 1),
    confidence: meta.confidence,
    estimatedRisk: meta.risk,
    category: meta.category,
    violationsFixed: meta.violationsFixed,
    complexity: 2,
  }
}

export function generateProposals(input: OptimizerInput): OptimizationProposal[] {
  const reelSet: StudioReelSet = { id: 'optimize', reels: input.reels.map((reel) => ({ ...reel, symbols: [...reel.symbols] })) }
  const validation = runConstraintEngine({
    reelSet,
    symbols: input.symbols,
    constraintDocument: input.constraintDocument,
  })
  const distribution = computeDistribution(stripsToReels(reelSet.reels))
  const proposals: OptimizationProposal[] = []
  const rng = createSeededRng(input.seed)

  for (const result of validation.results) {
    if (result.status === 'pass' || result.affectedPositions.length === 0) {
      continue
    }
    const from = result.affectedPositions[0]!
    const toReel =
      result.affectedReels.find((reel) => reel !== from.reelIndex) ??
      ((from.reelIndex + 1) % reelSet.reels.length)
    const toPos = Math.min(
      (reelSet.reels[toReel]?.symbols.length ?? 1) - 1,
      from.symbolIndex + 3,
    )
    const symbolId = reelSet.reels[from.reelIndex]?.symbols[from.symbolIndex] ?? 'symbol'
    const category: ProposalCategory =
      result.constraintType === 'min_distance' || result.constraintType === 'forbidden_adjacency'
        ? 'spacing'
        : 'constraint'
    const proposal = buildMoveProposal(input, reelSet, from.reelIndex, from.symbolIndex, toReel, toPos, {
      title: `Fix ${result.description}`,
      description: `Move ${symbolId} from Reel ${from.reelIndex + 1} position ${from.symbolIndex + 1} to Reel ${toReel + 1} position ${toPos + 1}`,
      reason: result.message,
      category,
      priority: result.status === 'error' ? 'critical' : 'high',
      expectedImprovement: ['remove violation', 'improve spacing', `Health +${result.status === 'error' ? 4 : 2}`],
      confidence: result.status === 'error' ? 92 : 78,
      risk: 'low',
      violationsFixed: 1,
    })
    if (proposal) {
      proposals.push(proposal)
    }
  }

  for (const entry of Object.values(input.constraintDocument.inventory)) {
    if (entry.totalTarget <= 0) {
      continue
    }
    const reelTotals = reelSet.reels.map((reel, reelIndex) => ({
      reelIndex,
      count: reel.symbols.filter((id) => id === entry.symbolId).length,
    }))
    const actual = reelTotals.reduce((sum, item) => sum + item.count, 0)
    const diff = entry.totalTarget - actual
    if (diff === 0) {
      continue
    }
    const donor = [...reelTotals].sort((a, b) => b.count - a.count)[0]
    const receiver = [...reelTotals].sort((a, b) => a.count - b.count)[0]
    if (!donor || !receiver || donor.count === 0 || donor.reelIndex === receiver.reelIndex) {
      continue
    }
    const donorPos = reelSet.reels[donor.reelIndex]?.symbols.findIndex((id) => id === entry.symbolId) ?? -1
    if (donorPos < 0) {
      continue
    }
    const insertPos = Math.floor(rng() * (reelSet.reels[receiver.reelIndex]?.symbols.length ?? 1))
    const proposal = buildMoveProposal(
      input,
      reelSet,
      donor.reelIndex,
      donorPos,
      receiver.reelIndex,
      insertPos,
      {
        title: `Rebalance ${entry.symbolId} inventory`,
        description: `Move one ${entry.symbolId} from Reel ${donor.reelIndex + 1} to Reel ${receiver.reelIndex + 1}`,
        reason: `Inventory target is ${entry.totalTarget}, current is ${actual}`,
        category: 'inventory',
        priority: Math.abs(diff) >= 3 ? 'high' : 'medium',
        expectedImprovement: ['Better balance', `Inventory gap ${diff}`, 'Health +3'],
        confidence: 85,
        risk: 'low',
        violationsFixed: 0,
      },
    )
    if (proposal) {
      proposals.push(proposal)
    }
  }

  for (const [symbolId, perReel] of Object.entries(distribution)) {
    const counts = Object.entries(perReel).map(([reelIndex, count]) => ({
      reelIndex: Number(reelIndex),
      count,
    }))
    if (counts.length < 2) {
      continue
    }
    const max = counts.reduce((best, item) => (item.count > best.count ? item : best), counts[0]!)
    const min = counts.reduce((best, item) => (item.count < best.count ? item : best), counts[0]!)
    if (max.count - min.count < 2) {
      continue
    }
    const fromPos =
      reelSet.reels[max.reelIndex]?.symbols.findIndex((id) => id === symbolId) ?? -1
    if (fromPos < 0) {
      continue
    }
    const toPos = Math.floor(rng() * (reelSet.reels[min.reelIndex]?.symbols.length ?? 1))
    const proposal = buildMoveProposal(
      input,
      reelSet,
      max.reelIndex,
      fromPos,
      min.reelIndex,
      toPos,
      {
        title: `Balance ${symbolId} across reels`,
        description: `Move one ${symbolId} from Reel ${max.reelIndex + 1} to Reel ${min.reelIndex + 1}`,
        reason: `${symbolId} is concentrated on Reel ${max.reelIndex + 1} (${max.count} vs ${min.count})`,
        category: 'distribution',
        priority: 'medium',
        expectedImprovement: ['Balance +3', 'Entropy +2', 'Health +2'],
        confidence: 80,
        risk: 'low',
        violationsFixed: 0,
      },
    )
    if (proposal) {
      proposals.push(proposal)
    }
  }

  for (const reel of reelSet.reels) {
    for (let index = 0; index < reel.symbols.length - 1; index += 1) {
      const current = reel.symbols[index]
      const next = reel.symbols[index + 1]
      if (!current || !next) {
        continue
      }
      const type = input.symbols[current]?.type
      if (type !== 'wild' && type !== 'scatter') {
        continue
      }
      if (current !== next) {
        continue
      }
      const swapReel = (reel.reelIndex + 1) % reelSet.reels.length
      const swapPos = Math.floor(rng() * (reelSet.reels[swapReel]?.symbols.length ?? 1))
      const proposal = buildSwapProposal(
        input,
        reelSet,
        reel.reelIndex,
        index,
        swapReel,
        swapPos,
        {
          title: `Reduce ${current} clustering`,
          description: `Swap clustered ${current} on Reel ${reel.reelIndex + 1} with Reel ${swapReel + 1}`,
          reason: `${current} appears consecutively on Reel ${reel.reelIndex + 1}`,
          category: 'clustering',
          priority: 'high',
          expectedImprovement: ['Better spacing', 'Lower clustering', 'Health +4'],
          confidence: 88,
          risk: 'medium',
          violationsFixed: 0,
        },
      )
      if (proposal) {
        proposals.push(proposal)
      }
    }
  }

  const seen = new Set<string>()
  return proposals.filter((proposal) => {
    if (seen.has(proposal.id)) {
      return false
    }
    seen.add(proposal.id)
    return true
  })
}
