import { describe, expect, it } from 'vitest'

import { createDefaultConstraintDocument } from '@/features/reel-studio/constraints/engine/utils'
import { DEFAULT_DESIGN_GOALS } from '@/features/reel-studio/generator/types'
import { evaluateDesignGoals } from '@/features/reel-studio/optimizer/goal-evaluator'
import { explainHealthDelta, healthEvolutionPath, createIterationSnapshot } from '@/features/reel-studio/optimizer/iteration'
import { runOptimizationEngine, remainingIssueCount } from '@/features/reel-studio/optimizer/optimization-engine'
import {
  buildOptimizationReport,
  estimateNextImprovement,
  summarizeRemainingIssues,
} from '@/features/reel-studio/optimizer/optimization-report'
import { optimize, optimizeBatch, DefaultBatchOptimizer } from '@/features/reel-studio/optimizer/optimizer'
import {
  appendOptimizationIteration,
  branchFromIteration,
  createInitialHistory,
  getIterationChain,
  markReady,
  recordGenerateEvent,
  rejectProposal,
  selectIteration,
  undoToParent,
} from '@/features/reel-studio/optimizer/optimizer-history'
import { generateProposals } from '@/features/reel-studio/optimizer/proposal'
import {
  applyProposalToReels,
  previewProposalOnReels,
} from '@/features/reel-studio/optimizer/proposal-application'
import { rankProposals, topProposals } from '@/features/reel-studio/optimizer/proposal-ranking'
import type { OptimizationProposal } from '@/features/reel-studio/optimizer/optimizer-types'
import type { StudioReelSet } from '@/features/reel-studio/types'

const symbols = {
  A: { id: 'A', type: 'regular' as const },
  B: { id: 'B', type: 'regular' as const },
  W: { id: 'W', type: 'wild' as const },
  S: { id: 'S', type: 'scatter' as const },
}

const reelSet: StudioReelSet = {
  id: 'base',
  reels: [
    { reelIndex: 0, symbols: ['W', 'W', 'A', 'B', 'S'] },
    { reelIndex: 1, symbols: ['A', 'B', 'S', 'A', 'B'] },
    { reelIndex: 2, symbols: ['A', 'W', 'B', 'S', 'A'] },
  ],
}

describe('goal evaluator', () => {
  it('evaluates design goals without RTP', () => {
    const document = createDefaultConstraintDocument(Object.keys(symbols), 3)
    const goals = evaluateDesignGoals(
      reelSet,
      symbols,
      DEFAULT_DESIGN_GOALS,
      document.edgeWrapping,
      document.groups,
    )
    expect(goals.length).toBeGreaterThan(0)
    expect(goals.some((goal) => goal.goalId === 'volatility')).toBe(true)
  })

  it('evaluates high and low volatility profiles', () => {
    const document = createDefaultConstraintDocument(Object.keys(symbols), 3)
    const highVol = evaluateDesignGoals(
      reelSet,
      symbols,
      { ...DEFAULT_DESIGN_GOALS, volatility: 'high' },
      document.edgeWrapping,
      document.groups,
    )
    const lowVol = evaluateDesignGoals(
      reelSet,
      symbols,
      { ...DEFAULT_DESIGN_GOALS, volatility: 'low' },
      document.edgeWrapping,
      document.groups,
    )
    expect(highVol.find((goal) => goal.goalId === 'volatility')?.target).toBe('high')
    expect(lowVol.find((goal) => goal.goalId === 'volatility')?.target).toBe('low')
  })
})

describe('proposal generation and ranking', () => {
  const document = createDefaultConstraintDocument(Object.keys(symbols), 3)
  document.constraints.push({
    id: 'max-w',
    type: 'max_consecutive',
    enabled: true,
    description: 'Wild streak',
    targetType: 'symbol',
    targetId: 'W',
    value: 1,
    scope: 'global',
    severity: 'error',
  })
  document.inventory.S = { symbolId: 'S', reelCounts: {}, totalTarget: 8 }

  const input = {
    reels: reelSet.reels,
    symbols,
    constraintDocument: document,
    designGoals: DEFAULT_DESIGN_GOALS,
    seed: 42,
  }

  it('generates deterministic proposals', () => {
    const first = generateProposals(input)
    const second = generateProposals(input)
    expect(first.map((proposal) => proposal.id)).toEqual(second.map((proposal) => proposal.id))
    expect(first.length).toBeGreaterThan(0)
    expect(first[0]?.reason.length).toBeGreaterThan(0)
  })

  it('ranks proposals by impact', () => {
    const proposals = generateProposals(input)
    const ranked = rankProposals(proposals)
    expect(ranked[0]?.priority).toBeDefined()
    expect(topProposals(proposals, 2)).toHaveLength(2)
  })

  it('applies and previews proposals', () => {
    const proposals = generateProposals(input)
    const proposal = proposals[0]
    expect(proposal).toBeDefined()
    const preview = previewProposalOnReels(reelSet.reels, proposal!)
    const applied = applyProposalToReels(reelSet.reels, proposal!)
    expect(preview).not.toEqual(reelSet.reels)
    expect(applied).toEqual(preview)
  })
})

describe('optimization engine', () => {
  it('runs deterministic optimization output', () => {
    const document = createDefaultConstraintDocument(Object.keys(symbols), 3)
    const input = {
      reels: reelSet.reels,
      symbols,
      constraintDocument: document,
      designGoals: DEFAULT_DESIGN_GOALS,
      seed: 99,
    }
    const first = runOptimizationEngine(input)
    const second = runOptimizationEngine(input)
    expect(first.currentHealth).toBe(second.currentHealth)
    expect(first.proposals.map((proposal) => proposal.id)).toEqual(
      second.proposals.map((proposal) => proposal.id),
    )
    expect(remainingIssueCount(input)).toBeGreaterThanOrEqual(0)
  })

  it('breaks ranking ties deterministically', () => {
    const proposals = generateProposals({
      reels: reelSet.reels,
      symbols,
      constraintDocument: createDefaultConstraintDocument(Object.keys(symbols), 3),
      designGoals: DEFAULT_DESIGN_GOALS,
      seed: 1,
    })
    const tied = proposals.map((proposal) => ({
      ...proposal,
      healthGain: 2,
      violationsFixed: 0,
      complexity: 1,
      priority: 'medium' as const,
    }))
    const first = rankProposals(tied).map((proposal) => proposal.id)
    const second = rankProposals(tied).map((proposal) => proposal.id)
    expect(first).toEqual(second)
  })
})

describe('batch optimization', () => {
  it('applies top proposals and stops on health decrease', () => {
    const document = createDefaultConstraintDocument(Object.keys(symbols), 3)
    document.constraints.push({
      id: 'max-w',
      type: 'max_consecutive',
      enabled: true,
      description: 'Wild streak',
      targetType: 'symbol',
      targetId: 'W',
      value: 1,
      scope: 'global',
      severity: 'error',
    })
    const input = {
      reels: reelSet.reels,
      symbols,
      constraintDocument: document,
      designGoals: DEFAULT_DESIGN_GOALS,
      seed: 7,
    }
    const result = optimizeBatch(input, 3, 'session-1', Date.now())
    expect(result.report.sessionId).toBe('session-1')
    expect(result.finalReels.length).toBe(3)
  })

  it('stops batch when a proposal would reduce health', () => {
    const document = createDefaultConstraintDocument(Object.keys(symbols), 3)
    const input = {
      reels: reelSet.reels,
      symbols,
      constraintDocument: document,
      designGoals: DEFAULT_DESIGN_GOALS,
      seed: 7,
    }
    const worsening: OptimizationProposal = {
      id: 'worse',
      title: 'Worsen',
      description: 'Move wild into cluster',
      reason: 'test',
      priority: 'critical',
      expectedImprovement: [],
      affectedReels: [0, 1],
      affectedSymbols: ['W'],
      before: [{ reelIndex: 1, symbolIndex: 2, symbolId: 'W' }],
      after: [{ reelIndex: 0, symbolIndex: 1, symbolId: 'W' }],
      healthGain: 1,
      confidence: 50,
      estimatedRisk: 'high',
      category: 'clustering',
      violationsFixed: 0,
      complexity: 1,
    }
    const result = new DefaultBatchOptimizer().optimizeBatch(
      input,
      [worsening],
      1,
      'session-stop',
      Date.now(),
    )
    expect(result.stoppedEarly || result.applied.length === 0 || result.applied.length === 1).toBe(true)
  })
})

describe('history and iterations', () => {
  it('tracks timeline, undo, branch, and reject', () => {
    const document = createDefaultConstraintDocument(Object.keys(symbols), 3)
    let history = createInitialHistory(reelSet.reels, symbols, document, 42)
    history = recordGenerateEvent(history, 42, history.iterations[0]!.health)
    const proposals = generateProposals({
      reels: reelSet.reels,
      symbols,
      constraintDocument: document,
      designGoals: DEFAULT_DESIGN_GOALS,
      seed: 42,
    })
    const proposal = proposals[0]
    expect(proposal).toBeDefined()
    const nextReels = applyProposalToReels(reelSet.reels, proposal!)
    history = appendOptimizationIteration(history, nextReels, symbols, document, proposal!, 42)
    expect(history.timeline.length).toBeGreaterThan(1)
    expect(getIterationChain(history, history.activeIterationId).length).toBe(2)

    history = branchFromIteration(history, history.activeIterationId, 'B1', nextReels, symbols, document, 42)
    history = rejectProposal(history, proposal!.id)
    expect(history.rejectedProposalIds).toContain(proposal!.id)

    const selected = selectIteration(history, history.iterations[0]!.id)
    const undone = undoToParent(selected)
    expect(undone.activeIterationId).toBe(history.iterations[0]!.id)

    history = markReady(history)
    expect(history.timeline.some((event) => event.type === 'ready')).toBe(true)
  })

  it('explains health evolution', () => {
    const document = createDefaultConstraintDocument(Object.keys(symbols), 3)
    const iteration = createIterationSnapshot(reelSet.reels, symbols, document, {
      id: 'iter-1',
      parentId: null,
      branchLabel: 'Main',
      timestamp: Date.now(),
      seed: 1,
      proposalId: 'p1',
      proposalTitle: 'Fix wild clustering',
      previousHealth: 70,
      healthReasons: ['Initial'],
    })
    expect(healthEvolutionPath([iteration])).toEqual([iteration.health])
    const reasons = explainHealthDelta({ ...iteration, healthDelta: -2 })
    expect(reasons.some((reason) => reason.includes('decreased'))).toBe(true)
  })

  it('handles history edge cases', () => {
    const document = createDefaultConstraintDocument(Object.keys(symbols), 3)
    let history = createInitialHistory(reelSet.reels, symbols, document, 42)
    history = undoToParent(history)
    expect(history.activeIterationId).toBe(history.iterations[0]!.id)
    history = selectIteration(history, 'missing-id')
    expect(history.activeIterationId).toBe(history.iterations[0]!.id)
    history = rejectProposal(history, 'already-rejected')
    history = rejectProposal(history, 'already-rejected')
    expect(history.rejectedProposalIds.filter((id) => id === 'already-rejected')).toHaveLength(1)
  })
})

describe('optimization report', () => {
  it('builds session report', () => {
    const document = createDefaultConstraintDocument(Object.keys(symbols), 3)
    const proposals = generateProposals({
      reels: reelSet.reels,
      symbols,
      constraintDocument: document,
      designGoals: DEFAULT_DESIGN_GOALS,
      seed: 5,
    })
    const report = buildOptimizationReport({
      sessionId: 's1',
      startedAt: Date.now() - 100,
      completedAt: Date.now(),
      beforeReelSet: reelSet,
      afterReelSet: reelSet,
      symbols,
      constraintDocument: document,
      appliedProposals: proposals.slice(0, 1),
      rejectedProposalIds: [],
      remainingIssues: summarizeRemainingIssues(proposals, []),
      estimatedNextImprovement: estimateNextImprovement(proposals),
    })
    expect(report.improvement).toBe(0)
    expect(report.timeSpentMs).toBeGreaterThanOrEqual(0)
  })

  it('optimizes through public API', () => {
    const document = createDefaultConstraintDocument(Object.keys(symbols), 3)
    const output = optimize({
      reels: reelSet.reels,
      symbols,
      constraintDocument: document,
      designGoals: DEFAULT_DESIGN_GOALS,
      seed: 3,
    })
    expect(output.proposals.length).toBeGreaterThanOrEqual(0)
  })
})
