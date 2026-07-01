import type {
  OptimizationIteration,
  OptimizationProposal,
  TimelineEvent,
} from '@/features/reel-studio/optimizer/optimizer-types'
import { createIterationSnapshot } from '@/features/reel-studio/optimizer/iteration'
import type { ConstraintDocument } from '@/features/reel-studio/constraints/types'
import type { StudioReelStrip, StudioSymbol } from '@/features/reel-studio/types'

export interface OptimizationHistoryState {
  iterations: OptimizationIteration[]
  timeline: TimelineEvent[]
  activeIterationId: string
  rejectedProposalIds: string[]
}

export function createInitialHistory(
  reels: StudioReelStrip[],
  symbols: Record<string, StudioSymbol>,
  constraintDocument: ConstraintDocument,
  seed: number,
  branchLabel = 'Main',
): OptimizationHistoryState {
  const timestamp = Date.now()
  const iterationId = `iter-root-${seed}`
  const iteration = createIterationSnapshot(reels, symbols, constraintDocument, {
    id: iterationId,
    parentId: null,
    branchLabel,
    timestamp,
    seed,
    proposalId: null,
    proposalTitle: null,
    previousHealth: 0,
    healthReasons: ['Initial design snapshot'],
  })
  return {
    iterations: [iteration],
    timeline: [
      {
        id: `timeline-design-${seed}`,
        type: 'design',
        timestamp,
        seed,
        iterationId,
        health: iteration.health,
        label: 'Design',
      },
    ],
    activeIterationId: iterationId,
    rejectedProposalIds: [],
  }
}

export function getActiveIteration(state: OptimizationHistoryState): OptimizationIteration {
  return (
    state.iterations.find((iteration) => iteration.id === state.activeIterationId) ??
    state.iterations[0]!
  )
}

export function getIterationChain(
  state: OptimizationHistoryState,
  iterationId: string,
): OptimizationIteration[] {
  const chain: OptimizationIteration[] = []
  let current = state.iterations.find((iteration) => iteration.id === iterationId)
  while (current) {
    chain.unshift(current)
    current = current.parentId
      ? state.iterations.find((iteration) => iteration.id === current!.parentId)
      : undefined
  }
  return chain
}

export function appendOptimizationIteration(
  state: OptimizationHistoryState,
  reels: StudioReelStrip[],
  symbols: Record<string, StudioSymbol>,
  constraintDocument: ConstraintDocument,
  proposal: OptimizationProposal,
  seed: number,
): OptimizationHistoryState {
  const parent = getActiveIteration(state)
  const timestamp = Date.now()
  const iterationId = `iter-${proposal.id}-${timestamp}`
  const iteration = createIterationSnapshot(reels, symbols, constraintDocument, {
    id: iterationId,
    parentId: parent.id,
    branchLabel: parent.branchLabel,
    timestamp,
    seed,
    proposalId: proposal.id,
    proposalTitle: proposal.title,
    previousHealth: parent.health,
    healthReasons: proposal.expectedImprovement,
  })
  return {
    ...state,
    iterations: [...state.iterations, iteration],
    activeIterationId: iterationId,
    timeline: [
      ...state.timeline,
      {
        id: `timeline-opt-${iterationId}`,
        type: 'optimize',
        timestamp,
        seed,
        iterationId,
        health: iteration.health,
        proposalId: proposal.id,
        label: proposal.title,
      },
    ],
  }
}

export function branchFromIteration(
  state: OptimizationHistoryState,
  iterationId: string,
  branchLabel: string,
  reels: StudioReelStrip[],
  symbols: Record<string, StudioSymbol>,
  constraintDocument: ConstraintDocument,
  seed: number,
): OptimizationHistoryState {
  const source =
    state.iterations.find((iteration) => iteration.id === iterationId) ?? getActiveIteration(state)
  const timestamp = Date.now()
  const newId = `iter-branch-${branchLabel}-${timestamp}`
  const iteration = createIterationSnapshot(reels, symbols, constraintDocument, {
    id: newId,
    parentId: source.id,
    branchLabel,
    timestamp,
    seed,
    proposalId: null,
    proposalTitle: null,
    previousHealth: source.health,
    healthReasons: [`Branched from ${source.branchLabel}`],
  })
  return {
    ...state,
    iterations: [...state.iterations, iteration],
    activeIterationId: newId,
    timeline: [
      ...state.timeline,
      {
        id: `timeline-branch-${newId}`,
        type: 'design',
        timestamp,
        seed,
        iterationId: newId,
        health: iteration.health,
        label: `Branch ${branchLabel}`,
      },
    ],
  }
}

export function undoToParent(state: OptimizationHistoryState): OptimizationHistoryState {
  const active = getActiveIteration(state)
  if (!active.parentId) {
    return state
  }
  return { ...state, activeIterationId: active.parentId }
}

export function selectIteration(
  state: OptimizationHistoryState,
  iterationId: string,
): OptimizationHistoryState {
  if (!state.iterations.some((iteration) => iteration.id === iterationId)) {
    return state
  }
  return { ...state, activeIterationId: iterationId }
}

export function rejectProposal(
  state: OptimizationHistoryState,
  proposalId: string,
): OptimizationHistoryState {
  if (state.rejectedProposalIds.includes(proposalId)) {
    return state
  }
  return {
    ...state,
    rejectedProposalIds: [...state.rejectedProposalIds, proposalId],
  }
}

export function recordGenerateEvent(
  state: OptimizationHistoryState,
  seed: number,
  health: number,
): OptimizationHistoryState {
  const active = getActiveIteration(state)
  const timestamp = Date.now()
  return {
    ...state,
    timeline: [
      ...state.timeline,
      {
        id: `timeline-generate-${timestamp}`,
        type: 'generate',
        timestamp,
        seed,
        iterationId: active.id,
        health,
        label: 'Generate candidates',
      },
    ],
  }
}

export function markReady(state: OptimizationHistoryState): OptimizationHistoryState {
  const active = getActiveIteration(state)
  const timestamp = Date.now()
  return {
    ...state,
    timeline: [
      ...state.timeline,
      {
        id: `timeline-ready-${timestamp}`,
        type: 'ready',
        timestamp,
        seed: active.seed,
        iterationId: active.id,
        health: active.health,
        label: 'Ready',
      },
    ],
  }
}
