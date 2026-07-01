import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import type { WorkspaceMode } from '@/features/reel-studio/layout/types'

const MODES: Array<{ id: WorkspaceMode; label: string }> = [
  { id: 'design', label: 'Design' },
  { id: 'symbols', label: 'Symbols' },
  { id: 'constraints', label: 'Constraints' },
  { id: 'optimization', label: 'Optimization' },
]

export function WorkspaceContextPanel({
  mode,
  onModeChange,
  children,
}: {
  mode: WorkspaceMode
  onModeChange: (mode: WorkspaceMode) => void
  children: React.ReactNode
}) {
  return (
    <div className="flex h-full flex-col">
      <Tabs
        value={mode}
        onValueChange={(value) => onModeChange(value as WorkspaceMode)}
        className="shrink-0 border-b border-border/20 px-4 pt-4"
      >
        <TabsList className="h-9 w-full bg-transparent p-0">
          {MODES.map((item) => (
            <TabsTrigger
              key={item.id}
              value={item.id}
              className="flex-1 rounded-none border-b-2 border-transparent px-2 pb-3 pt-1 text-xs font-medium text-muted-foreground shadow-none transition-colors duration-150 data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:text-primary data-[state=active]:shadow-none"
            >
              {item.label}
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>
      <div className="flex-1 overflow-y-auto px-4 py-4">{children}</div>
    </div>
  )
}
