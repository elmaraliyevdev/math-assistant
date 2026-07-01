import { Plus, Trash2 } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { useConstraintStudio } from '@/features/reel-studio/constraints/context/constraint-studio-context'
import { useReelStudio } from '@/features/reel-studio/context/reel-studio-context'

export function SymbolGroupsPanel() {
  const { document } = useReelStudio()
  const { constraintDocument, addGroup, updateGroup, removeGroup } = useConstraintStudio()
  const symbolIds = Object.keys(document.symbols)

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm">Symbol groups</CardTitle>
        <Button
          type="button"
          size="sm"
          variant="outline"
          onClick={() =>
            addGroup({
              id: `group-${Date.now()}`,
              name: 'Custom group',
              symbolIds: [],
            })
          }
        >
          <Plus className="h-3.5 w-3.5" />
          Add
        </Button>
      </CardHeader>
      <CardContent className="space-y-3">
        {constraintDocument.groups.length === 0 ? (
          <p className="text-xs text-muted-foreground">No groups yet. Presets create default groups.</p>
        ) : (
          constraintDocument.groups.map((group) => (
            <div key={group.id} className="space-y-2 rounded-md border p-2">
              <div className="flex items-center gap-2">
                <Input
                  className="h-8 text-xs"
                  value={group.name}
                  onChange={(event) => updateGroup(group.id, { name: event.target.value })}
                />
                <Button
                  type="button"
                  size="icon"
                  variant="ghost"
                  className="h-8 w-8"
                  onClick={() => removeGroup(group.id)}
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </Button>
              </div>
              <div className="flex flex-wrap gap-1">
                {symbolIds.map((symbolId) => {
                  const active = group.symbolIds.includes(symbolId)
                  return (
                    <button
                      key={symbolId}
                      type="button"
                      className={`rounded border px-2 py-0.5 text-[10px] ${active ? 'border-primary bg-primary/10' : 'border-muted'}`}
                      onClick={() => {
                        const symbolIdsNext = active
                          ? group.symbolIds.filter((id) => id !== symbolId)
                          : [...group.symbolIds, symbolId]
                        updateGroup(group.id, { symbolIds: symbolIdsNext })
                      }}
                    >
                      {symbolId}
                    </button>
                  )
                })}
              </div>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  )
}
