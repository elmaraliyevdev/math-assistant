import { ChevronDown } from 'lucide-react'
import { useState, type ReactNode } from 'react'

import { useInspectorAccordion } from '@/components/studio/InspectorAccordion'
import { cn } from '@/lib/utils'

export function CollapsibleSection({
  id,
  title,
  subtitle,
  defaultOpen = false,
  badge,
  children,
  className,
  accordion = false,
}: {
  id?: string
  title: string
  subtitle?: string
  defaultOpen?: boolean
  badge?: ReactNode
  children: ReactNode
  className?: string
  /** When true, only one section in the parent accordion may be open */
  accordion?: boolean
}) {
  const accordionContext = useInspectorAccordion()
  const [localOpen, setLocalOpen] = useState(defaultOpen)

  const open = accordion && id && accordionContext
    ? accordionContext.openId === id
    : localOpen

  const toggle = () => {
    if (accordion && id && accordionContext) {
      accordionContext.toggle(id)
      return
    }
    setLocalOpen((value) => !value)
  }

  return (
    <section className={cn('border-b border-border/20 last:border-b-0', className)}>
      <button
        type="button"
        className="flex w-full items-start justify-between gap-3 py-3 text-left transition-colors hover:text-foreground"
        onClick={toggle}
      >
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">{title}</span>
            {badge}
          </div>
          {subtitle && !open ? (
            <p className="mt-0.5 truncate text-xs text-muted-foreground">{subtitle}</p>
          ) : null}
        </div>
        <ChevronDown
          className={cn(
            'mt-0.5 h-5 w-5 shrink-0 text-foreground/70 transition-transform duration-200',
            open && 'rotate-180',
          )}
          strokeWidth={2.25}
        />
      </button>
      <div
        className={cn(
          'grid transition-all duration-200 ease-out',
          open ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0',
        )}
      >
        <div className="overflow-hidden">
          <div className="pb-4">{children}</div>
        </div>
      </div>
    </section>
  )
}
