import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'

import { runConstraintEngine } from '@/features/reel-studio/constraints/engine'
import { createDefaultConstraintDocument } from '@/features/reel-studio/constraints/engine/utils'
import { computeAdvancedStatistics } from '@/features/reel-studio/constraints/lib/advanced-statistics'
import { BUILTIN_PRESETS, hydratePresetGroups } from '@/features/reel-studio/constraints/lib/presets'
import {
  duplicatePreset,
  exportPreset,
  importPreset,
  parseConstraintDocument,
  serializeConstraintDocument,
} from '@/features/reel-studio/constraints/lib/serialize'
import {
  createUndoStack,
  pushUndoStack,
  redoStack,
  undoStack,
  type UndoStackState,
} from '@/features/reel-studio/constraints/lib/undo-stack'
import type {
  ConstraintDocument,
  ConstraintPreset,
  ConstraintRule,
  ConstraintValidationReport,
  SymbolGroup,
  ValidationResultItem,
} from '@/features/reel-studio/constraints/types'
import { useReelStudio } from '@/features/reel-studio/context/reel-studio-context'

const CUSTOM_PRESETS_KEY = 'reel-studio-custom-presets'
const LAYOUT_KEY = 'reel-studio-design-layout'

export interface DesignLayoutState {
  leftWidth: number
  rightWidth: number
  showInventory: boolean
  showGroups: boolean
  showConstraints: boolean
}

const DEFAULT_LAYOUT: DesignLayoutState = {
  leftWidth: 280,
  rightWidth: 320,
  showInventory: true,
  showGroups: true,
  showConstraints: true,
}

interface ConstraintStudioContextValue {
  constraintDocument: ConstraintDocument
  validation: ConstraintValidationReport
  advancedStats: ReturnType<typeof computeAdvancedStatistics>
  customPresets: ConstraintPreset[]
  layout: DesignLayoutState
  canUndo: boolean
  canRedo: boolean
  focusedViolation: ValidationResultItem | null
  setFocusedViolation: (item: ValidationResultItem | null) => void
  setEdgeWrapping: (value: boolean) => void
  updateConstraintDocument: (updater: (current: ConstraintDocument) => ConstraintDocument) => void
  addConstraint: (rule: ConstraintRule) => void
  updateConstraint: (ruleId: string, patch: Partial<ConstraintRule>) => void
  duplicateConstraint: (ruleId: string) => void
  removeConstraint: (ruleId: string) => void
  addGroup: (group: SymbolGroup) => void
  updateGroup: (groupId: string, patch: Partial<SymbolGroup>) => void
  removeGroup: (groupId: string) => void
  updateInventoryCount: (symbolId: string, reelIndex: number, count: number) => void
  updateInventoryTotal: (symbolId: string, total: number) => void
  loadPreset: (presetId: string) => void
  saveCustomPreset: (name: string) => void
  duplicateCustomPreset: (presetId: string, name: string) => void
  exportCustomPreset: (presetId: string) => string
  importCustomPreset: (raw: string) => void
  listPresets: () => ConstraintPreset[]
  undo: () => void
  redo: () => void
  updateLayout: (patch: Partial<DesignLayoutState>) => void
  exportConstraintDocument: () => string
  importConstraintDocument: (raw: string) => void
}

const ConstraintStudioContext = createContext<ConstraintStudioContextValue | null>(null)

function loadCustomPresets(): ConstraintPreset[] {
  try {
    const raw = localStorage.getItem(CUSTOM_PRESETS_KEY)
    return raw ? (JSON.parse(raw) as ConstraintPreset[]) : []
  } catch {
    return []
  }
}

function loadLayout(): DesignLayoutState {
  try {
    const raw = localStorage.getItem(LAYOUT_KEY)
    return raw ? { ...DEFAULT_LAYOUT, ...JSON.parse(raw) } : DEFAULT_LAYOUT
  } catch {
    return DEFAULT_LAYOUT
  }
}

export function ConstraintStudioProvider({ children }: { children: ReactNode }) {
  const { document } = useReelStudio()
  const reelSet = document.reelSets[document.activeReelSetId]
  const reelCount = reelSet?.reels.length ?? 0
  const symbolIds = Object.keys(document.symbols)

  const [undoState, setUndoState] = useState<UndoStackState<ConstraintDocument>>(() =>
    createUndoStack(createDefaultConstraintDocument(symbolIds, reelCount)),
  )
  const [customPresets, setCustomPresets] = useState<ConstraintPreset[]>(loadCustomPresets)
  const [layout, setLayout] = useState<DesignLayoutState>(loadLayout)
  const [focusedViolation, setFocusedViolation] = useState<ValidationResultItem | null>(null)

  useEffect(() => {
    setUndoState((current) => {
      const nextInventory = { ...current.present.inventory }
      let changed = false
      for (const symbolId of symbolIds) {
        if (!nextInventory[symbolId]) {
          changed = true
          nextInventory[symbolId] = createDefaultConstraintDocument([symbolId], reelCount)
            .inventory[symbolId]!
        }
      }
      if (!changed) {
        return current
      }
      return { ...current, present: { ...current.present, inventory: nextInventory } }
    })
  }, [symbolIds.join(','), reelCount])

  const constraintDocument = undoState.present

  const validation = useMemo(() => {
    if (!reelSet) {
      return {
        results: [],
        summary: { pass: 0, warning: 0, error: 0, byCategory: {} },
        violationsByPosition: {},
      }
    }
    return runConstraintEngine({
      reelSet,
      symbols: document.symbols,
      constraintDocument,
    })
  }, [constraintDocument, document.symbols, reelSet])

  const advancedStats = useMemo(() => {
    if (!reelSet) {
      return computeAdvancedStatistics(
        { id: 'empty', reels: [] },
        document.symbols,
        constraintDocument.groups,
        constraintDocument.edgeWrapping,
      )
    }
    return computeAdvancedStatistics(
      reelSet,
      document.symbols,
      constraintDocument.groups,
      constraintDocument.edgeWrapping,
    )
  }, [constraintDocument.edgeWrapping, constraintDocument.groups, document.symbols, reelSet])

  const commitDocument = useCallback((updater: (current: ConstraintDocument) => ConstraintDocument) => {
    setUndoState((current) => pushUndoStack(current, updater(current.present)))
  }, [])

  const undo = useCallback(() => {
    setUndoState((current) => undoStack(current) ?? current)
  }, [])

  const redo = useCallback(() => {
    setUndoState((current) => redoStack(current) ?? current)
  }, [])

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      const meta = event.metaKey || event.ctrlKey
      if (!meta || event.key.toLowerCase() !== 'z') {
        return
      }
      event.preventDefault()
      if (event.shiftKey) {
        redo()
      } else {
        undo()
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [redo, undo])

  const value: ConstraintStudioContextValue = {
    constraintDocument,
    validation,
    advancedStats,
    customPresets,
    layout,
    canUndo: undoState.past.length > 0,
    canRedo: undoState.future.length > 0,
    focusedViolation,
    setFocusedViolation,
    setEdgeWrapping: (edgeWrapping) => commitDocument((current) => ({ ...current, edgeWrapping })),
    updateConstraintDocument: commitDocument,
    addConstraint: (rule) =>
      commitDocument((current) => ({ ...current, constraints: [...current.constraints, rule] })),
    updateConstraint: (ruleId, patch) =>
      commitDocument((current) => ({
        ...current,
        constraints: current.constraints.map((rule) =>
          rule.id === ruleId ? { ...rule, ...patch } : rule,
        ),
      })),
    duplicateConstraint: (ruleId) =>
      commitDocument((current) => {
        const source = current.constraints.find((rule) => rule.id === ruleId)
        if (!source) {
          return current
        }
        return {
          ...current,
          constraints: [
            ...current.constraints,
            {
              ...source,
              id: `${source.id}-copy-${Date.now()}`,
              description: `${source.description} (copy)`,
            },
          ],
        }
      }),
    removeConstraint: (ruleId) =>
      commitDocument((current) => ({
        ...current,
        constraints: current.constraints.filter((rule) => rule.id !== ruleId),
      })),
    addGroup: (group) =>
      commitDocument((current) => ({ ...current, groups: [...current.groups, group] })),
    updateGroup: (groupId, patch) =>
      commitDocument((current) => ({
        ...current,
        groups: current.groups.map((group) =>
          group.id === groupId ? { ...group, ...patch } : group,
        ),
      })),
    removeGroup: (groupId) =>
      commitDocument((current) => ({
        ...current,
        groups: current.groups.filter((group) => group.id !== groupId),
      })),
    updateInventoryCount: (symbolId, reelIndex, count) =>
      commitDocument((current) => {
        const entry = current.inventory[symbolId]
        if (!entry) {
          return current
        }
        const reelCounts = { ...entry.reelCounts, [String(reelIndex)]: count }
        const totalTarget = Object.values(reelCounts).reduce((sum, value) => sum + value, 0)
        return {
          ...current,
          inventory: {
            ...current.inventory,
            [symbolId]: { ...entry, reelCounts, totalTarget },
          },
        }
      }),
    updateInventoryTotal: (symbolId, total) =>
      commitDocument((current) => {
        const entry = current.inventory[symbolId]
        if (!entry) {
          return current
        }
        return {
          ...current,
          inventory: {
            ...current.inventory,
            [symbolId]: { ...entry, totalTarget: total },
          },
        }
      }),
    loadPreset: (presetId) => {
      const preset = [...BUILTIN_PRESETS, ...customPresets].find((item) => item.id === presetId)
      if (!preset) {
        return
      }
      const hydrated = hydratePresetGroups(preset, document.symbols)
      setUndoState((current) => pushUndoStack(current, hydrated))
    },
    saveCustomPreset: (name) => {
      const preset: ConstraintPreset = {
        id: `custom-${Date.now()}`,
        name,
        description: 'User saved preset',
        builtIn: false,
        document: {
          version: constraintDocument.version,
          edgeWrapping: constraintDocument.edgeWrapping,
          groups: constraintDocument.groups,
          inventory: constraintDocument.inventory,
          constraints: constraintDocument.constraints,
        },
      }
      const next = [...customPresets, preset]
      setCustomPresets(next)
      localStorage.setItem(CUSTOM_PRESETS_KEY, JSON.stringify(next))
    },
    duplicateCustomPreset: (presetId, name) => {
      const source = customPresets.find((item) => item.id === presetId)
      if (!source) {
        return
      }
      const next = [...customPresets, duplicatePreset(source, `custom-${Date.now()}`, name)]
      setCustomPresets(next)
      localStorage.setItem(CUSTOM_PRESETS_KEY, JSON.stringify(next))
    },
    exportCustomPreset: (presetId) => {
      const preset = [...BUILTIN_PRESETS, ...customPresets].find((item) => item.id === presetId)
      return preset ? exportPreset(preset) : ''
    },
    importCustomPreset: (raw) => {
      const preset = importPreset(raw)
      const next = [...customPresets, preset]
      setCustomPresets(next)
      localStorage.setItem(CUSTOM_PRESETS_KEY, JSON.stringify(next))
    },
    listPresets: () => [...BUILTIN_PRESETS, ...customPresets],
    undo,
    redo,
    updateLayout: (patch) => {
      setLayout((current) => {
        const next = { ...current, ...patch }
        localStorage.setItem(LAYOUT_KEY, JSON.stringify(next))
        return next
      })
    },
    exportConstraintDocument: () => serializeConstraintDocument(constraintDocument),
    importConstraintDocument: (raw) => {
      const parsed = parseConstraintDocument(raw)
      setUndoState((current) => pushUndoStack(current, parsed))
    },
  }

  return (
    <ConstraintStudioContext.Provider value={value}>{children}</ConstraintStudioContext.Provider>
  )
}

export function useConstraintStudio() {
  const context = useContext(ConstraintStudioContext)
  if (!context) {
    throw new Error('useConstraintStudio must be used within ConstraintStudioProvider')
  }
  return context
}
