import { Link } from '@tanstack/react-router'
import { Bot } from 'lucide-react'
import type { ReactNode } from 'react'

import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import { cn } from '@/lib/utils'

interface AiHelpLinkProps {
  prompt: string
  className?: string
}

export function AiHelpLink({ prompt, className }: AiHelpLinkProps) {
  return (
    <Button variant="ghost" size="sm" className={cn('h-8 gap-1.5 text-xs', className)} asChild>
      <Link to="/assistant" search={{ prompt }}>
        <Bot className="h-3.5 w-3.5" />
        Ask AI
      </Link>
    </Button>
  )
}

export function SettingsSectionHeader({
  title,
  description,
  aiPrompt,
  actions,
}: {
  title: string
  description?: string
  aiPrompt?: string
  actions?: ReactNode
}) {
  return (
    <div className="mb-4 flex flex-col gap-3 border-b border-border/60 pb-4 sm:flex-row sm:items-start sm:justify-between">
      <div className="space-y-1">
        <div className="flex flex-wrap items-center gap-2">
          <h2 className="text-xl font-semibold tracking-tight">{title}</h2>
          {aiPrompt ? <AiHelpLink prompt={aiPrompt} /> : null}
        </div>
        {description ? (
          <p className="text-sm text-muted-foreground">{description}</p>
        ) : null}
      </div>
      {actions ? <div className="flex shrink-0 flex-wrap gap-2">{actions}</div> : null}
    </div>
  )
}

export function SettingsFieldGroup({
  title,
  description,
  children,
  className,
}: {
  title: string
  description?: string
  children: ReactNode
  className?: string
}) {
  return (
    <section className={cn('space-y-3', className)}>
      <div>
        <h3 className="text-sm font-medium">{title}</h3>
        {description ? (
          <p className="text-xs text-muted-foreground">{description}</p>
        ) : null}
      </div>
      {children}
    </section>
  )
}

export function SettingsDangerZone({
  title,
  description,
  children,
}: {
  title: string
  description: string
  children: ReactNode
}) {
  return (
    <section className="rounded-lg border border-destructive/30 bg-destructive/5 p-4">
      <div className="mb-3">
        <h3 className="text-sm font-medium text-destructive">{title}</h3>
        <p className="text-xs text-muted-foreground">{description}</p>
      </div>
      {children}
    </section>
  )
}

export function SettingSwitchRow({
  label,
  description,
  checked,
  onCheckedChange,
  disabled,
}: {
  label: string
  description: string
  checked: boolean
  onCheckedChange: (checked: boolean) => void
  disabled?: boolean
}) {
  return (
    <div className="flex items-start justify-between gap-4 rounded-md border border-border/60 px-3 py-2.5">
      <div className="min-w-0 space-y-0.5">
        <p className="text-sm font-medium">{label}</p>
        <p className="text-xs text-muted-foreground">{description}</p>
      </div>
      <Switch
        aria-label={label}
        checked={checked}
        onCheckedChange={onCheckedChange}
        disabled={disabled}
      />
    </div>
  )
}
