import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from 'react'

import { buildDiffSet, diffReels } from '@/features/reel-studio/generator/candidate'
import { buildGeneratorInput, generateCandidates } from '@/features/reel-studio/generator/generator'
import { buildSmartSuggestions, computeDesignHealth } from '@/features/reel-studio/generator/health'
import { mergeHeatmapLayers } from '@/features/reel-studio/generator/heatmap'
import {
  DEFAULT_DESIGN_GOALS,
  type DesignGoals,
  type GeneratedCandidate,
  type GenerationReport,
} from '@/features/reel-studio/generator/types'
import { useConstraintStudio } from '@/features/reel-studio/constraints/context/constraint-studio-context'
import { useReelStudio } from '@/features/reel-studio/context/reel-studio-context'

interface GeneratorContextValue {
  designGoals: DesignGoals
  seed: number
  candidateCount: number
  report: GenerationReport | null
  selectedCandidateId: string | null
  previewCandidate: GeneratedCandidate | null
  diffPositions: Set<string>
  heatmapOverlay: Record<string, { wild: number; scatter: number; violation: number }>
  isGenerating: boolean
  designHealth: ReturnType<typeof computeDesignHealth>
  suggestions: ReturnType<typeof buildSmartSuggestions>
  setDesignGoals: (patch: Partial<DesignGoals>) => void
  setSeed: (seed: number) => void
  setCandidateCount: (count: number) => void
  generate: () => void
  selectCandidate: (candidateId: string | null) => void
  applyCandidate: () => void
  clearPreview: () => void
}

const GeneratorContext = createContext<GeneratorContextValue | null>(null)

export function GeneratorProvider({ children }: { children: ReactNode }) {
  const { document, replaceReels } = useReelStudio()
  const { constraintDocument } = useConstraintStudio()
  const [designGoals, setDesignGoalsState] = useState<DesignGoals>(DEFAULT_DESIGN_GOALS)
  const [seed, setSeed] = useState(42)
  const [candidateCount, setCandidateCount] = useState(3)
  const [report, setReport] = useState<GenerationReport | null>(null)
  const [selectedCandidateId, setSelectedCandidateId] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)

  const activeReelSet = document.reelSets[document.activeReelSetId]

  const previewCandidate = useMemo(() => {
    if (!report || !selectedCandidateId) {
      return null
    }
    return report.candidates.find((candidate) => candidate.id === selectedCandidateId) ?? null
  }, [report, selectedCandidateId])

  const diffPositions = useMemo(() => {
    if (!previewCandidate || !activeReelSet) {
      return new Set<string>()
    }
    return buildDiffSet(diffReels(activeReelSet.reels, previewCandidate.reels))
  }, [activeReelSet, previewCandidate])

  const heatmapOverlay = useMemo(() => {
    if (!previewCandidate) {
      return {}
    }
    return mergeHeatmapLayers(previewCandidate.heatmaps)
  }, [previewCandidate])

  const designHealth = useMemo(() => {
    if (!activeReelSet) {
      return { overallScore: 0, metrics: [], recommendations: [] }
    }
    return computeDesignHealth(activeReelSet, document.symbols, constraintDocument)
  }, [activeReelSet, constraintDocument, document.symbols])

  const suggestions = useMemo(() => {
    if (!activeReelSet) {
      return []
    }
    return buildSmartSuggestions(activeReelSet, document.symbols, constraintDocument)
  }, [activeReelSet, constraintDocument, document.symbols])

  const generate = useCallback(() => {
    if (!activeReelSet) {
      return
    }
    setIsGenerating(true)
    const reelLengths =
      activeReelSet.reels.length > 0
        ? activeReelSet.reels.map((reel) => reel.symbols.length || designGoals.reelLength)
        : Array.from({ length: designGoals.reelCount }, () => designGoals.reelLength)

    const input = buildGeneratorInput({
      reelCount: reelLengths.length,
      reelLengths,
      symbols: document.symbols,
      constraintDocument,
      designGoals,
      seed,
      candidateCount,
    })
    const nextReport = generateCandidates(input)
    setReport(nextReport)
    setSelectedCandidateId(nextReport.ranking[0] ?? null)
    setIsGenerating(false)
  }, [
    activeReelSet,
    candidateCount,
    constraintDocument,
    designGoals,
    document.symbols,
    seed,
  ])

  const applyCandidate = useCallback(() => {
    if (!previewCandidate) {
      return
    }
    replaceReels(previewCandidate.reels)
    setSelectedCandidateId(null)
    setReport(null)
  }, [previewCandidate, replaceReels])

  const value: GeneratorContextValue = {
    designGoals,
    seed,
    candidateCount,
    report,
    selectedCandidateId,
    previewCandidate,
    diffPositions,
    heatmapOverlay,
    isGenerating,
    designHealth,
    suggestions,
    setDesignGoals: (patch) => setDesignGoalsState((current) => ({ ...current, ...patch })),
    setSeed,
    setCandidateCount,
    generate,
    selectCandidate: setSelectedCandidateId,
    applyCandidate,
    clearPreview: () => {
      setSelectedCandidateId(null)
      setReport(null)
    },
  }

  return <GeneratorContext.Provider value={value}>{children}</GeneratorContext.Provider>
}

export function useGeneratorStudio() {
  const context = useContext(GeneratorContext)
  if (!context) {
    throw new Error('useGeneratorStudio must be used within GeneratorProvider')
  }
  return context
}
