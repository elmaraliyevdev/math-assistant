import { ArrowUp, Paperclip, Sparkles } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'

import { Button } from '@/components/ui/button'
import { QUICK_ACTIONS, SLASH_COMMANDS } from '@/features/assistant/lib/prompts'
import { cn } from '@/lib/utils'

export function AssistantComposer({
  value,
  onChange,
  onSubmit,
  loading,
  onQuickAction,
  onUseContext,
}: {
  value: string
  onChange: (value: string) => void
  onSubmit: () => void
  loading?: boolean
  onQuickAction: (prompt: string) => void
  onUseContext: () => void
}) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const [showCommands, setShowCommands] = useState(false)

  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`
  }, [value])

  const filteredCommands = value.startsWith('/')
    ? SLASH_COMMANDS.filter((item) => item.command.startsWith(value.trim().toLowerCase()))
    : []

  return (
    <div className="border-t border-border/40 bg-background/95 p-4 backdrop-blur-sm">
      <div className="mb-2 flex flex-wrap gap-2">
        {QUICK_ACTIONS.map((action) => (
          <button
            key={action}
            type="button"
            disabled={loading}
            onClick={() => onQuickAction(action)}
            className="rounded-full border border-border/40 px-3 py-1 text-xs transition-colors hover:border-primary/30 hover:bg-primary/5 disabled:opacity-50"
          >
            {action}
          </button>
        ))}
      </div>

      {showCommands && filteredCommands.length > 0 ? (
        <div className="mb-2 rounded-xl border border-border/40 bg-card p-2">
          {filteredCommands.map((item) => (
            <button
              key={item.command}
              type="button"
              className="flex w-full items-center justify-between rounded-lg px-3 py-2 text-left text-sm hover:bg-muted/50"
              onClick={() => {
                onChange(item.prompt)
                setShowCommands(false)
              }}
            >
              <span className="font-mono text-primary">{item.command}</span>
              <span className="truncate text-muted-foreground">{item.prompt}</span>
            </button>
          ))}
        </div>
      ) : null}

      <div className="flex items-end gap-2 rounded-2xl border border-border/40 bg-card px-3 py-2 shadow-sm">
        <div className="flex shrink-0 items-center gap-1 pb-1">
          <Button type="button" size="icon" variant="ghost" className="h-8 w-8" disabled>
            <Paperclip className="h-4 w-4" />
            <span className="sr-only">Attach</span>
          </Button>
          <Button
            type="button"
            size="icon"
            variant="ghost"
            className="h-8 w-8"
            onClick={onUseContext}
            title="Use current context"
          >
            <Sparkles className="h-4 w-4" />
            <span className="sr-only">Use context</span>
          </Button>
        </div>
        <textarea
          ref={textareaRef}
          rows={1}
          value={value}
          onChange={(event) => {
            onChange(event.target.value)
            setShowCommands(event.target.value.startsWith('/'))
          }}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
              event.preventDefault()
              if (!loading && value.trim()) onSubmit()
            }
          }}
          placeholder="Ask about RTP, volatility, certification, or type / for commands…"
          className={cn(
            'max-h-40 min-h-[24px] flex-1 resize-none bg-transparent py-2 text-sm outline-none',
            'placeholder:text-muted-foreground',
          )}
        />
        <Button
          type="button"
          size="icon"
          className="h-9 w-9 shrink-0 rounded-xl"
          disabled={loading || !value.trim()}
          onClick={onSubmit}
        >
          <ArrowUp className="h-4 w-4" />
          <span className="sr-only">Send</span>
        </Button>
      </div>
    </div>
  )
}
