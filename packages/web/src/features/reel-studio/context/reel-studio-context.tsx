import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from 'react'

import {
  addSymbolToReel,
  duplicateSymbolOnReel,
  moveSymbolBetweenReels,
  moveSymbolWithinReel,
  parsePaletteId,
  parseReelContainerId,
  parseSlotId,
  removeSymbolFromReel,
  replaceActiveReelSet,
  setActiveReelSetId,
} from '@/features/reel-studio/lib/reel-mutations'
import { mergeReelSetsIntoCanonical } from '@/features/reel-studio/lib/serialize-canonical'
import { computeReelSetStats } from '@/features/reel-studio/lib/statistics'
import type { ReelSetStats, ReelStudioDocument, StudioReelStrip } from '@/features/reel-studio/types'

interface ReelStudioContextValue {
  document: ReelStudioDocument
  stats: ReelSetStats
  previewJson: Record<string, unknown>
  setActiveReelSet: (reelSetId: string) => void
  handleDragEnd: (activeId: string, overId: string | null) => void
  addSymbol: (reelIndex: number, symbolId: string) => void
  removeSymbol: (reelIndex: number, symbolIndex: number) => void
  duplicateSymbol: (reelIndex: number, symbolIndex: number) => void
  replaceReels: (reels: StudioReelStrip[]) => void
}

const ReelStudioContext = createContext<ReelStudioContextValue | null>(null)

export function ReelStudioProvider({
  initialDocument,
  children,
}: {
  initialDocument: ReelStudioDocument
  children: ReactNode
}) {
  const [document, setDocument] = useState(initialDocument)

  const stats = useMemo(() => {
    const reelSet = document.reelSets[document.activeReelSetId]
    if (!reelSet) {
      return {
        reelSetId: document.activeReelSetId,
        reels: [],
        totals: { totalSymbols: 0, symbolCounts: [], duplicateSymbolIds: [] },
      }
    }
    return computeReelSetStats(reelSet)
  }, [document])

  const previewJson = useMemo(
    () => mergeReelSetsIntoCanonical(document.originalCanonicalJson, document.reelSets),
    [document],
  )

  const handleDragEnd = useCallback((activeId: string, overId: string | null) => {
    if (!overId) {
      return
    }

    const paletteSymbol = parsePaletteId(activeId)
    if (paletteSymbol) {
      const targetReel = parseReelContainerId(overId)
      const targetSlot = parseSlotId(overId)
      if (targetReel !== null) {
        setDocument((current) => addSymbolToReel(current, targetReel, paletteSymbol))
        return
      }
      if (targetSlot) {
        setDocument((current) =>
          addSymbolToReel(
            current,
            targetSlot.reelIndex,
            paletteSymbol,
            targetSlot.symbolIndex,
          ),
        )
      }
      return
    }

    const source = parseSlotId(activeId)
    if (!source) {
      return
    }

    const targetSlot = parseSlotId(overId)
    if (targetSlot) {
      setDocument((current) => {
        if (source.reelIndex === targetSlot.reelIndex) {
          return moveSymbolWithinReel(
            current,
            source.reelIndex,
            source.symbolIndex,
            targetSlot.symbolIndex,
          )
        }
        return moveSymbolBetweenReels(
          current,
          source.reelIndex,
          source.symbolIndex,
          targetSlot.reelIndex,
          targetSlot.symbolIndex,
        )
      })
      return
    }

    const targetReel = parseReelContainerId(overId)
    if (targetReel !== null) {
      setDocument((current) => {
        const reelSet = current.reelSets[current.activeReelSetId]
        const reel = reelSet?.reels.find((item) => item.reelIndex === targetReel)
        const position = reel?.symbols.length ?? 0
        if (source.reelIndex === targetReel) {
          return moveSymbolWithinReel(
            current,
            source.reelIndex,
            source.symbolIndex,
            position,
          )
        }
        return moveSymbolBetweenReels(
          current,
          source.reelIndex,
          source.symbolIndex,
          targetReel,
          position,
        )
      })
    }
  }, [])

  const value: ReelStudioContextValue = {
    document,
    stats,
    previewJson,
    setActiveReelSet: (reelSetId) => {
      setDocument((current) => setActiveReelSetId(current, reelSetId))
    },
    handleDragEnd,
    addSymbol: (reelIndex, symbolId) => {
      setDocument((current) => addSymbolToReel(current, reelIndex, symbolId))
    },
    removeSymbol: (reelIndex, symbolIndex) => {
      setDocument((current) => removeSymbolFromReel(current, reelIndex, symbolIndex))
    },
    duplicateSymbol: (reelIndex, symbolIndex) => {
      setDocument((current) => duplicateSymbolOnReel(current, reelIndex, symbolIndex))
    },
    replaceReels: (reels) => {
      setDocument((current) => replaceActiveReelSet(current, reels))
    },
  }

  return (
    <ReelStudioContext.Provider value={value}>{children}</ReelStudioContext.Provider>
  )
}

export function useReelStudio() {
  const context = useContext(ReelStudioContext)
  if (!context) {
    throw new Error('useReelStudio must be used within ReelStudioProvider')
  }
  return context
}

export function useReelStudioDocument() {
  return useReelStudio().document
}

export function useReelStudioPreview() {
  return useReelStudio().previewJson
}
