import type { ReactNode } from 'react'
import { ChevronDown, ChevronRight, Copy } from 'lucide-react'
import { useMemo, useState } from 'react'

import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { toast } from '@/lib/toast'

interface JsonViewerProps {
  value: unknown
  className?: string
}

export function JsonViewer({ value, className }: JsonViewerProps) {
  const text = useMemo(() => JSON.stringify(value, null, 2), [value])

  return (
    <div className={cn('rounded-lg border bg-muted/30', className)}>
      <div className="flex items-center justify-between border-b px-3 py-2">
        <span className="text-xs font-medium text-muted-foreground">Canonical JSON</span>
        <Button
          variant="ghost"
          size="sm"
          onClick={async () => {
            await navigator.clipboard.writeText(text)
            toast.success('JSON copied to clipboard')
          }}
        >
          <Copy className="h-4 w-4" />
          Copy
        </Button>
      </div>
      <div className="max-h-[480px] overflow-auto p-3 font-mono text-xs leading-relaxed">
        <JsonNode value={value} name="root" depth={0} />
      </div>
    </div>
  )
}

function JsonNode({
  value,
  name,
  depth,
}: {
  value: unknown
  name: string
  depth: number
}) {
  const [expanded, setExpanded] = useState(depth < 2)

  if (value === null) {
    return <Line name={name} value="null" type="null" />
  }

  if (Array.isArray(value)) {
    return (
      <Collapsible
        name={name}
        label={`Array(${value.length})`}
        expanded={expanded}
        onToggle={() => setExpanded((v) => !v)}
        depth={depth}
      >
        {expanded &&
          value.map((item, index) => (
            <div key={index} className="pl-4">
              <JsonNode value={item} name={String(index)} depth={depth + 1} />
            </div>
          ))}
      </Collapsible>
    )
  }

  if (typeof value === 'object') {
    const entries = Object.entries(value as Record<string, unknown>)
    return (
      <Collapsible
        name={name}
        label={`{${entries.length} keys}`}
        expanded={expanded}
        onToggle={() => setExpanded((v) => !v)}
        depth={depth}
      >
        {expanded &&
          entries.map(([key, child]) => (
            <div key={key} className="pl-4">
              <JsonNode value={child} name={key} depth={depth + 1} />
            </div>
          ))}
      </Collapsible>
    )
  }

  return <Line name={name} value={JSON.stringify(value)} type={typeof value} />
}

function Collapsible({
  name,
  label,
  expanded,
  onToggle,
  children,
}: {
  name: string
  label: string
  expanded: boolean
  onToggle: () => void
  depth: number
  children: ReactNode
}) {
  return (
    <div>
      <button
        type="button"
        className="flex items-center gap-1 text-left hover:text-primary"
        onClick={onToggle}
      >
        {expanded ? (
          <ChevronDown className="h-3 w-3" />
        ) : (
          <ChevronRight className="h-3 w-3" />
        )}
        <span className="text-sky-600 dark:text-sky-400">{name}</span>
        <span className="text-muted-foreground">{label}</span>
      </button>
      {expanded && children}
    </div>
  )
}

function Line({
  name,
  value,
  type,
}: {
  name: string
  value: string
  type: string
}) {
  const valueClass =
    type === 'string'
      ? 'text-emerald-600 dark:text-emerald-400'
      : type === 'number'
        ? 'text-amber-600 dark:text-amber-400'
        : type === 'boolean'
          ? 'text-violet-600 dark:text-violet-400'
          : 'text-muted-foreground'

  return (
    <div className="flex flex-wrap gap-1 py-0.5">
      <span className="text-sky-600 dark:text-sky-400">{name}:</span>
      <span className={valueClass}>{value}</span>
    </div>
  )
}
