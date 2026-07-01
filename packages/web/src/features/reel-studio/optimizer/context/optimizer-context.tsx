import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'

import { buildDiffSet, diffReels } from '@/features/reel-studio/generator/candidate'
import { useConstraintStudio } from '@/features/reel-studio/constraints/context/constraint-studio-context'
import { useReelStudio } from '@/features/reel-studio/context/reel-studio-context'
import { useGeneratorStudio } from '@/features/reel-studio/generator/context/generator-context'
import { healthEvolutionPath } from '@/features/reel-studio/optimizer/iteration'
import {
  appendOptimizationIteration,
  branchFromIteration,
  createInitialHistory,
  getActiveIteration,
  getIterationChain,
  markReady,
  rejectProposal,
  selectIteration,
  undoToParent,
  type OptimizationHistoryState,
} from '@/features/reel-studio/optimizer/optimizer-history'
import { optimize, optimizeBatch } from '@/features/reel-studio/optimizer/optimizer'
import { previewProposalOnReels } from '@/features/reel-studio/optimizer/proposal-application'
import { topProposals } from '@/features/reel-studio/optimizer/proposal-ranking'
import type {
  OptimizationProposal,
  OptimizationReport,
  OptimizerOutput,
} from '@/features/reel-studio/optimizer/optimizer-types'

interface OptimizerContextValue {
  output: OptimizerOutput
  proposals: OptimizationProposal[]
  previewProposal: OptimizationProposal | null
  previewDiffPositions: Set<string>
  history: OptimizationHistoryState
  activeIteration: ReturnType<typeof getActiveIteration>
  iterationChain: ReturnType<typeof getIterationChain>
  healthEvolution: number[]
  lastReport: OptimizationReport | null
  isOptimizing: boolean
  refreshProposals: () => void
  preview: (proposalId: string | null) => void
  applyProposal: (proposalId: string) => void
  rejectProposalById: (proposalId: string) => void
  optimizeTop: (count: number | 'all') => void
  undoIteration: () => void
  selectIterationById: (iterationId: string) => void
  branchIteration: (iterationId: string, branchLabel: string) => void
  markDesignReady: () => void
}

const OptimizerContext = createContext<OptimizerContextValue | null>(null)

export function OptimizerProvider({ children }: { children: ReactNode }) {
  const { document, replaceReels } = useReelStudio()
  const { constraintDocument } = useConstraintStudio()
  const { designGoals, seed } = useGeneratorStudio()
  const [previewProposalId, setPreviewProposalId] = useState<string | null>(null)
  const [history, setHistory] = useState<OptimizationHistoryState | null>(null)
  const [lastReport, setLastReport] = useState<OptimizationReport | null>(null)
  const [isOptimizing, setIsOptimizing] = useState(false)
  const [output, setOutput] = useState<OptimizerOutput>({
    proposals: [],
    goalEvaluation: [],
    currentHealth: 0,
  })

  const activeReelSet = document.reelSets[document.activeReelSetId]

  useEffect(() => {
    if (!activeReelSet) {
      return
    }
    setHistory(createInitialHistory(activeReelSet.reels, document.symbols, constraintDocument, seed))
  }, [document.activeReelSetId, seed])

  const optimizerInput = useMemo(() => {
    if (!activeReelSet) {
      return null
    }
    return {
      reels: activeReelSet.reels,
      symbols: document.symbols,
      constraintDocument,
      designGoals,
      seed,
    }
  }, [activeReelSet, constraintDocument, designGoals, document.symbols, seed])

  const refreshProposals = useCallback(() => {
    if (!optimizerInput) {
      return
    }
    setOutput(optimize(optimizerInput))
  }, [optimizerInput])

  useEffect(() => {
    refreshProposals()
  }, [refreshProposals])

  const proposals = useMemo(
    () =>
      topProposals(
        output.proposals.filter(
          (proposal) => !(history?.rejectedProposalIds.includes(proposal.id) ?? false),
        ),
        output.proposals.length,
      ),
    [history?.rejectedProposalIds, output.proposals],
  )

  const previewProposal = useMemo(
    () => proposals.find((proposal) => proposal.id === previewProposalId) ?? null,
    [previewProposalId, proposals],
  )

  const previewDiffPositions = useMemo(() => {
    if (!previewProposal || !activeReelSet) {
      return new Set<string>()
    }
    const previewReels = previewProposalOnReels(activeReelSet.reels, previewProposal)
    return buildDiffSet(diffReels(activeReelSet.reels, previewReels))
  }, [activeReelSet, previewProposal])

  const activeIteration = history ? getActiveIteration(history) : null
  const iterationChain = history && activeIteration ? getIterationChain(history, activeIteration.id) : []
  const healthEvolution = healthEvolutionPath(iterationChain)

  const applyProposal = useCallback(
    (proposalId: string) => {
      if (!optimizerInput || !activeReelSet || !history) {
        return
      }
      const proposal = output.proposals.find((item) => item.id === proposalId)
      if (!proposal) {
        return
      }
      const nextReels = previewProposalOnReels(activeReelSet.reels, proposal)
      replaceReels(nextReels)
      setHistory((current) =>
        current
          ? appendOptimizationIteration(
              current,
              nextReels,
              document.symbols,
              constraintDocument,
              proposal,
              seed,
            )
          : current,
      )
      setPreviewProposalId(null)
      refreshProposals()
    },
    [
      activeReelSet,
      constraintDocument,
      document.symbols,
      history,
      optimizerInput,
      output.proposals,
      refreshProposals,
      replaceReels,
      seed,
    ],
  )

  const optimizeTop = useCallback(
    (count: number | 'all') => {
      if (!optimizerInput || !history) {
        return
      }
      setIsOptimizing(true)
      const startedAt = Date.now()
      const sessionId = `session-${seed}-${startedAt}`
      const result = optimizeBatch(optimizerInput, count, sessionId, startedAt)
      if (result.applied.length > 0) {
        replaceReels(result.finalReels)
        let nextHistory = history
        for (const proposal of result.applied) {
          nextHistory = appendOptimizationIteration(
            nextHistory,
            getActiveIteration(nextHistory).reels,
            document.symbols,
            constraintDocument,
            proposal,
            seed,
          )
        }
        setHistory(nextHistory)
      }
      setLastReport(result.report)
      setPreviewProposalId(null)
      refreshProposals()
      setIsOptimizing(false)
    },
    [
      activeReelSet,
      constraintDocument,
      document.symbols,
      history,
      optimizerInput,
      refreshProposals,
      replaceReels,
      seed,
    ],
  )

  const value: OptimizerContextValue = {
    output,
    proposals,
    previewProposal,
    previewDiffPositions,
    history: history ?? {
      iterations: [],
      timeline: [],
      activeIterationId: '',
      rejectedProposalIds: [],
    },
    activeIteration: activeIteration ?? {
      id: 'empty',
      parentId: null,
      branchLabel: 'Main',
      timestamp: 0,
      seed,
      health: 0,
      healthDelta: 0,
      proposalId: null,
      proposalTitle: null,
      reels: [],
      distribution: {},
      constraintSummary: { pass: 0, warning: 0, error: 0 },
      healthReasons: [],
    },
    iterationChain,
    healthEvolution,
    lastReport,
    isOptimizing,
    refreshProposals,
    preview: setPreviewProposalId,
    applyProposal,
    rejectProposalById: (proposalId) => {
      setHistory((current) => (current ? rejectProposal(current, proposalId) : current))
      if (previewProposalId === proposalId) {
        setPreviewProposalId(null)
      }
    },
    optimizeTop,
    undoIteration: () => {
      setHistory((current) => {
        if (!current) {
          return current
        }
        const undone = undoToParent(current)
        const iteration = getActiveIteration(undone)
        replaceReels(iteration.reels)
        return undone
      })
      refreshProposals()
    },
    selectIterationById: (iterationId) => {
      setHistory((current) => {
        if (!current) {
          return current
        }
        const next = selectIteration(current, iterationId)
        const iteration = getActiveIteration(next)
        replaceReels(iteration.reels)
        return next
      })
      refreshProposals()
    },
    branchIteration: (iterationId, branchLabel) => {
      if (!activeReelSet) {
        return
      }
      const source = history?.iterations.find((iteration) => iteration.id === iterationId)
      const reels = source?.reels ?? activeReelSet.reels
      setHistory((current) =>
        current
          ? branchFromIteration(
              current,
              iterationId,
              branchLabel,
              reels,
              document.symbols,
              constraintDocument,
              seed,
            )
          : current,
      )
      refreshProposals()
    },
    markDesignReady: () => {
      setHistory((current) => (current ? markReady(current) : current))
    },
  }

  return <OptimizerContext.Provider value={value}>{children}</OptimizerContext.Provider>
}

export function useOptimizerStudio() {
  const context = useContext(OptimizerContext)
  if (!context) {
    throw new Error('useOptimizerStudio must be used within OptimizerProvider')
  }
  return context
}
