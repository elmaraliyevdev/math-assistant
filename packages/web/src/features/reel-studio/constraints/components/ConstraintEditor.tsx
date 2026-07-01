import { CheckCircle2, Copy, Plus, Trash2, XCircle } from 'lucide-react'
import { useMemo, useState } from 'react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useConstraintStudio } from '@/features/reel-studio/constraints/context/constraint-studio-context'
import type { ConstraintRule, ConstraintType } from '@/features/reel-studio/constraints/types'

const CONSTRAINT_TYPES: { value: ConstraintType; label: string }[] = [
  { value: 'min_count', label: 'Minimum count' },
  { value: 'max_count', label: 'Maximum count' },
  { value: 'exact_count', label: 'Exact count' },
  { value: 'min_consecutive', label: 'Minimum consecutive' },
  { value: 'max_consecutive', label: 'Maximum consecutive' },
  { value: 'min_distance', label: 'Minimum distance' },
  { value: 'forbidden_adjacency', label: 'Forbidden adjacency' },
  { value: 'allowed_adjacency', label: 'Allowed adjacency' },
  { value: 'reel_specific_count', label: 'Reel-specific count' },
]

function statusForRule(ruleId: string, results: ReturnType<typeof useConstraintStudio>['validation']['results']) {
  return results.find((item) => item.constraintId === ruleId)?.status ?? 'pass'
}

export function ConstraintEditor() {
  const {
    constraintDocument,
    validation,
    addConstraint,
    updateConstraint,
    duplicateConstraint,
    removeConstraint,
  } = useConstraintStudio()
  const [filter, setFilter] = useState('')
  const [sortBy, setSortBy] = useState<'type' | 'status'>('type')

  const rows = useMemo(() => {
    const filtered = constraintDocument.constraints.filter((rule) => {
      const haystack = `${rule.type} ${rule.description} ${rule.targetId}`.toLowerCase()
      return haystack.includes(filter.toLowerCase())
    })
    return filtered.sort((a, b) => {
      if (sortBy === 'status') {
        return statusForRule(a.id, validation.results).localeCompare(
          statusForRule(b.id, validation.results),
        )
      }
      return a.type.localeCompare(b.type)
    })
  }, [constraintDocument.constraints, filter, sortBy, validation.results])

  const addBlank = () => {
    const rule: ConstraintRule = {
      id: `rule-${Date.now()}`,
      type: 'min_count',
      enabled: true,
      description: 'New constraint',
      targetType: 'symbol',
      targetId: '',
      value: 1,
      scope: 'global',
      severity: 'error',
    }
    addConstraint(rule)
  }

  return (
    <Card>
      <CardHeader className="flex flex-row flex-wrap items-center justify-between gap-2 pb-2">
        <CardTitle className="text-sm">Constraint editor</CardTitle>
        <div className="flex flex-wrap items-center gap-2">
          <Input
            className="h-8 w-40 text-xs"
            placeholder="Search…"
            value={filter}
            onChange={(event) => setFilter(event.target.value)}
          />
          <Select value={sortBy} onValueChange={(value) => setSortBy(value as 'type' | 'status')}>
            <SelectTrigger className="h-8 w-28 text-xs">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="type">Sort: type</SelectItem>
              <SelectItem value="status">Sort: status</SelectItem>
            </SelectContent>
          </Select>
          <Button type="button" size="sm" variant="outline" onClick={addBlank}>
            <Plus className="h-3.5 w-3.5" />
            Add
          </Button>
        </div>
      </CardHeader>
      <CardContent className="overflow-x-auto">
        <table className="w-full min-w-[900px] text-xs">
          <thead>
            <tr className="border-b text-left text-muted-foreground">
              <th className="py-2 pr-2">Type</th>
              <th className="py-2 pr-2">Target</th>
              <th className="py-2 pr-2">Operator</th>
              <th className="py-2 pr-2">Value</th>
              <th className="py-2 pr-2">Status</th>
              <th className="py-2 pr-2">Description</th>
              <th className="py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((rule) => {
              const status = statusForRule(rule.id, validation.results)
              return (
                <tr key={rule.id} className="border-b border-muted/40">
                  <td className="py-2 pr-2">
                    <Select
                      value={rule.type}
                      onValueChange={(value) =>
                        updateConstraint(rule.id, { type: value as ConstraintType })
                      }
                    >
                      <SelectTrigger className="h-8 text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {CONSTRAINT_TYPES.map((item) => (
                          <SelectItem key={item.value} value={item.value}>
                            {item.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </td>
                  <td className="py-2 pr-2">
                    <Input
                      className="h-8 text-xs"
                      value={rule.targetId}
                      onChange={(event) =>
                        updateConstraint(rule.id, { targetId: event.target.value })
                      }
                    />
                  </td>
                  <td className="py-2 pr-2 capitalize">{rule.scope.replace('_', ' ')}</td>
                  <td className="py-2 pr-2">
                    <Input
                      className="h-8 w-16 text-xs"
                      type="number"
                      value={rule.value}
                      onChange={(event) =>
                        updateConstraint(rule.id, { value: Number(event.target.value) })
                      }
                    />
                  </td>
                  <td className="py-2 pr-2">
                    <StatusBadge status={status} />
                  </td>
                  <td className="py-2 pr-2">
                    <Input
                      className="h-8 text-xs"
                      value={rule.description}
                      onChange={(event) =>
                        updateConstraint(rule.id, { description: event.target.value })
                      }
                    />
                  </td>
                  <td className="py-2">
                    <div className="flex gap-1">
                      <Button
                        type="button"
                        size="icon"
                        variant="ghost"
                        className="h-7 w-7"
                        onClick={() => duplicateConstraint(rule.id)}
                      >
                        <Copy className="h-3.5 w-3.5" />
                      </Button>
                      <Button
                        type="button"
                        size="icon"
                        variant="ghost"
                        className="h-7 w-7 text-destructive"
                        onClick={() => removeConstraint(rule.id)}
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </CardContent>
    </Card>
  )
}

function StatusBadge({ status }: { status: string }) {
  if (status === 'pass') {
    return (
      <Badge className="bg-emerald-100 text-emerald-900" variant="secondary">
        <CheckCircle2 className="mr-1 h-3 w-3" />
        PASS
      </Badge>
    )
  }
  if (status === 'warning') {
    return (
      <Badge className="bg-amber-100 text-amber-900" variant="secondary">
        WARNING
      </Badge>
    )
  }
  return (
    <Badge className="bg-red-100 text-red-900" variant="secondary">
      <XCircle className="mr-1 h-3 w-3" />
      ERROR
    </Badge>
  )
}
