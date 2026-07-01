import { Plus } from 'lucide-react'
import { useState } from 'react'

import { CollapsibleSection } from '@/components/studio/CollapsibleSection'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useConstraintStudio } from '@/features/reel-studio/constraints/context/constraint-studio-context'
import type { ConstraintRule } from '@/features/reel-studio/constraints/types'
import { useReelStudio } from '@/features/reel-studio/context/reel-studio-context'

type SentenceTemplate =
  | 'forbidden_adjacency'
  | 'min_distance'
  | 'max_consecutive'

const TEMPLATES: { id: SentenceTemplate; label: string }[] = [
  { id: 'forbidden_adjacency', label: 'cannot appear next to' },
  { id: 'min_distance', label: 'must be at least N symbols apart' },
  { id: 'max_consecutive', label: 'cannot appear more than N in a row' },
]

export function ConstraintSentenceBuilder() {
  const { document } = useReelStudio()
  const { constraintDocument, addConstraint } = useConstraintStudio()
  const [template, setTemplate] = useState<SentenceTemplate>('forbidden_adjacency')
  const [targetId, setTargetId] = useState('')
  const [secondaryId, setSecondaryId] = useState('')
  const [value, setValue] = useState(5)

  const symbolOptions = Object.keys(document.symbols)
  const groupOptions = constraintDocument.groups

  const addRule = () => {
    if (!targetId) {
      return
    }
    const rule: ConstraintRule = {
      id: `rule-${Date.now()}`,
      type: template,
      enabled: true,
      description:
        template === 'forbidden_adjacency'
          ? `${targetId} cannot appear next to ${secondaryId || targetId}`
          : template === 'min_distance'
            ? `${targetId} must be at least ${value} symbols apart`
            : `${targetId} max ${value} consecutive`,
      targetType: groupOptions.some((group) => group.id === targetId) ? 'group' : 'symbol',
      targetId,
      secondaryTargetType: secondaryId
        ? groupOptions.some((group) => group.id === secondaryId)
          ? 'group'
          : 'symbol'
        : undefined,
      secondaryTargetId: secondaryId || undefined,
      value: template === 'forbidden_adjacency' ? 1 : value,
      scope: 'global',
      severity: 'error',
    }
    addConstraint(rule)
    setTargetId('')
    setSecondaryId('')
  }

  return (
    <CollapsibleSection title="Constraints" subtitle="Build rules as readable sentences" defaultOpen>
      <div className="space-y-3 rounded-lg bg-muted/20 p-3 ring-1 ring-border/30">
        <div className="flex flex-wrap items-center gap-2 text-sm">
          <Select value={targetId} onValueChange={setTargetId}>
            <SelectTrigger className="w-[120px]">
              <SelectValue placeholder="Symbol" />
            </SelectTrigger>
            <SelectContent>
              {symbolOptions.map((id) => (
                <SelectItem key={id} value={id}>
                  {id}
                </SelectItem>
              ))}
              {groupOptions.map((group) => (
                <SelectItem key={group.id} value={group.id}>
                  {group.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={template} onValueChange={(next) => setTemplate(next as SentenceTemplate)}>
            <SelectTrigger className="w-[220px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {TEMPLATES.map((item) => (
                <SelectItem key={item.id} value={item.id}>
                  {item.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {template === 'forbidden_adjacency' ? (
            <>
              <span className="text-muted-foreground">or</span>
              <Select value={secondaryId} onValueChange={setSecondaryId}>
                <SelectTrigger className="w-[120px]">
                  <SelectValue placeholder="Other" />
                </SelectTrigger>
                <SelectContent>
                  {symbolOptions.map((id) => (
                    <SelectItem key={id} value={id}>
                      {id}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </>
          ) : (
            <Input
              type="number"
              className="w-20"
              value={value}
              onChange={(event) => setValue(Number(event.target.value))}
            />
          )}
        </div>

        <Button type="button" size="sm" onClick={addRule}>
          <Plus className="mr-1 h-4 w-4" />
          Add rule
        </Button>
      </div>
    </CollapsibleSection>
  )
}
