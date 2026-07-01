import {
  DndContext,
  DragOverlay,
  useSensor,
  useSensors,
  closestCenter,
  type DragEndEvent,
  type DragOverEvent,
  type DragStartEvent,
} from '@dnd-kit/core'
import { useNavigate } from '@tanstack/react-router'
import { useEffect, useState } from 'react'

import { SymbolPalette } from '@/features/reel-studio/components/SymbolPalette'
import { ReelEditor } from '@/features/reel-studio/components/ReelEditor'
import { AdvancedStatisticsPanel } from '@/features/reel-studio/constraints/components/AdvancedStatisticsPanel'
import { ConstraintEditor } from '@/features/reel-studio/constraints/components/ConstraintEditor'
import { ConstraintPresetManager } from '@/features/reel-studio/constraints/components/ConstraintPresetManager'
import { ReelViolationBridge } from '@/features/reel-studio/constraints/context/reel-violation-context'
import { SymbolGroupsPanel } from '@/features/reel-studio/constraints/components/SymbolGroupsPanel'
import { SymbolInventoryPanel } from '@/features/reel-studio/constraints/components/SymbolInventoryPanel'
import { ValidationSidebar } from '@/features/reel-studio/constraints/components/ValidationSidebar'
import { useConstraintStudio } from '@/features/reel-studio/constraints/context/constraint-studio-context'
import { ConstraintSentenceBuilder } from '@/features/reel-studio/generator/components/ConstraintSentenceBuilder'
import { ConstraintVisualizationPanel } from '@/features/reel-studio/generator/components/ConstraintVisualizationPanel'
import { DistributionDashboard } from '@/features/reel-studio/generator/components/DistributionDashboard'
import { GenerationReportPanel } from '@/features/reel-studio/generator/components/GenerationReportPanel'
import { ReelBalanceDashboard } from '@/features/reel-studio/generator/components/ReelBalanceDashboard'
import { SymbolInventoryDashboard } from '@/features/reel-studio/generator/components/SymbolInventoryDashboard'
import { useReelStudio } from '@/features/reel-studio/context/reel-studio-context'
import { useStudioKeyboard } from '@/features/reel-studio/hooks/use-studio-keyboard'
import { useReelStudioSave } from '@/features/reel-studio/hooks/use-reel-studio-save'
import { DesignInspector } from '@/features/reel-studio/layout/DesignInspector'
import { LiveStatsBar } from '@/features/reel-studio/layout/LiveStatsBar'
import {
  StudioActivityBar,
  StudioActivityBarMobile,
} from '@/features/reel-studio/layout/StudioActivityBar'
import { StudioBottomDock } from '@/features/reel-studio/layout/StudioBottomDock'
import { StudioCanvasProvider, useStudioCanvas } from '@/features/reel-studio/layout/studio-canvas-context'
import { StudioEditorToolbar } from '@/features/reel-studio/layout/StudioEditorToolbar'
import { StudioHeader } from '@/features/reel-studio/layout/StudioHeader'
import {
  StudioAiCopilot,
  SymbolInspector,
} from '@/features/reel-studio/layout/StudioInspectorPanels'
import type { BottomDrawerTab, WorkspaceMode } from '@/features/reel-studio/layout/types'
import {
  GoalEvaluationPanel,
  OptimizationReportPanel,
  ProposalDetailPanel,
} from '@/features/reel-studio/optimizer/components/ProposalDetailPanel'
import { HealthEvolutionChart } from '@/features/reel-studio/optimizer/components/HealthEvolutionChart'
import { OptimizationPanel } from '@/features/reel-studio/optimizer/components/OptimizationPanel'
import {
  IterationSelector,
  OptimizationTimeline,
} from '@/features/reel-studio/optimizer/components/OptimizationTimeline'
import {
  resolveDragEndIds,
  resolveDragOverlayLabel,
} from '@/features/reel-studio/lib/drag-events'
import { StudioWorkspace } from '@/features/reel-studio/workspace/StudioWorkspace'
import { StudioPointerSensor } from '@/features/reel-studio/workspace/studio-pointer-sensor'

function StudioCanvas({ activeLabel }: { activeLabel: string | null }) {
  return (
    <main className="relative min-h-0 min-w-0 overflow-hidden bg-[var(--studio-canvas-bg,hsl(var(--muted)/0.15))]">
      <StudioWorkspace>
        <ReelViolationBridge>
          <ReelEditor />
        </ReelViolationBridge>
      </StudioWorkspace>
      <DragOverlay dropAnimation={{ duration: 150, easing: 'ease-out' }}>
        {activeLabel ? (
          <div className="rounded-lg bg-background px-4 py-2 text-sm shadow-xl ring-2 ring-primary/40">
            {activeLabel}
          </div>
        ) : null}
      </DragOverlay>
    </main>
  )
}

function StudioKeyboardLayer({
  gameId,
  onOpenAi,
}: {
  gameId: string
  onOpenAi: () => void
}) {
  const navigate = useNavigate()
  const { document } = useReelStudio()
  const { canUndo, canRedo, undo, redo } = useConstraintStudio()
  const save = useReelStudioSave(gameId)

  useStudioKeyboard({
    onSave: () => save.mutate(document),
    onUndo: undo,
    onRedo: redo,
    onOpenGame: () => navigate({ to: '/reel-studio' }),
    onOpenAi,
    canUndo,
    canRedo,
  })

  return null
}

function RightPanelContent({
  mode,
  gameId,
  versionId,
}: {
  mode: WorkspaceMode
  gameId: string
  versionId: string
}) {
  const { document } = useReelStudio()

  if (mode === 'ai') {
    return <StudioAiCopilot gameId={gameId} versionId={versionId} />
  }
  if (mode === 'design') {
    return <DesignInspector />
  }
  if (mode === 'symbols') {
    return <SymbolPalette symbols={document.symbols} />
  }
  if (mode === 'constraints') {
    return (
      <div className="space-y-6 px-4 py-4">
        <ConstraintSentenceBuilder />
        <SymbolInventoryDashboard />
        <SymbolInventoryPanel />
        <SymbolGroupsPanel />
        <ConstraintEditor />
        <ConstraintPresetManager />
      </div>
    )
  }
  if (mode === 'optimization') {
    return (
      <div className="px-4 py-4">
        <OptimizationPanel />
      </div>
    )
  }
  return null
}

export function DesignStudioLayout({
  gameId,
  versionId,
  gameName,
  versionNumber,
}: {
  gameId: string
  versionId: string
  gameName: string
  versionNumber: number
}) {
  const { document, handleDragEnd } = useReelStudio()
  const [activeLabel, setActiveLabel] = useState<string | null>(null)
  const [mode, setMode] = useState<WorkspaceMode>('design')
  const [drawerTab, setDrawerTab] = useState<BottomDrawerTab | null>(null)
  const [dragOverId, setDragOverId] = useState<string | null>(null)
  const sensors = useSensors(
    useSensor(StudioPointerSensor, { activationConstraint: { distance: 6 } }),
  )

  const onDragStart = (event: DragStartEvent) => {
    setActiveLabel(resolveDragOverlayLabel(event, document.symbols))
  }

  const onDragOver = (event: DragOverEvent) => {
    setDragOverId(event.over ? String(event.over.id) : null)
  }

  const onDragEnd = (event: DragEndEvent) => {
    setActiveLabel(null)
    setDragOverId(null)
    const { activeId, overId } = resolveDragEndIds(event)
    handleDragEnd(activeId, overId)
  }

  const openDock = (tab: BottomDrawerTab) => {
    setDrawerTab((current) => (current === tab ? null : tab))
  }

  return (
    <StudioCanvasProvider>
      <StudioKeyboardLayer gameId={gameId} onOpenAi={() => setMode('ai')} />
      <DragOverSync dragOverId={dragOverId} />
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragStart={onDragStart}
        onDragOver={onDragOver}
        onDragEnd={onDragEnd}
      >
        <div data-studio-root className="studio-workspace flex h-full min-h-0 flex-col">
          <StudioHeader
            gameId={gameId}
            versionId={versionId}
            gameName={gameName}
            versionNumber={versionNumber}
          />
          <StudioEditorToolbar gameId={gameId} versionId={versionId} />
          <LiveStatsBar />
          <StudioActivityBarMobile mode={mode} onModeChange={setMode} />

          <div className="grid min-h-0 flex-1 grid-rows-[minmax(0,1fr)_auto] overflow-hidden">
            <div className="grid min-h-0 grid-cols-1 overflow-hidden lg:grid-cols-[48px_minmax(0,1fr)_minmax(280px,32%)]">
              <div className="hidden lg:contents">
                <StudioActivityBar
                  mode={mode}
                  onModeChange={setMode}
                  onOpenDock={openDock}
                />
              </div>

              <StudioCanvas activeLabel={activeLabel} />

              <aside className="studio-context hidden min-h-0 overflow-hidden border-l border-border/20 bg-muted/10 lg:flex lg:flex-col">
                <SymbolInspector />
                <div className="min-h-0 flex-1 overflow-y-auto">
                  <RightPanelContent mode={mode} gameId={gameId} versionId={versionId} />
                </div>
              </aside>
            </div>

            <StudioBottomDock
              activeTab={drawerTab}
              onTabChange={setDrawerTab}
              validation={<ValidationSidebar />}
              simulation={<GenerationReportPanel />}
              statistics={
                <>
                  <DistributionDashboard />
                  <ReelBalanceDashboard />
                  <AdvancedStatisticsPanel />
                </>
              }
              console={
                <>
                  <OptimizationTimeline />
                  <IterationSelector />
                  <GoalEvaluationPanel />
                  <ProposalDetailPanel />
                  <OptimizationReportPanel />
                  <HealthEvolutionChart />
                  <ConstraintVisualizationPanel />
                </>
              }
            />
          </div>
        </div>
      </DndContext>
    </StudioCanvasProvider>
  )
}

function DragOverSync({ dragOverId }: { dragOverId: string | null }) {
  const { setActiveDropTargetId } = useStudioCanvas()

  useEffect(() => {
    setActiveDropTargetId(dragOverId)
  }, [dragOverId, setActiveDropTargetId])

  return null
}
