import { Link } from '@tanstack/react-router'

import { PageHeader, PageLayout } from '@/components/design-system'
import {
  SETTINGS_SECTIONS,
  type SettingsSectionId,
} from '@/features/settings/settings-sections'
import { cn } from '@/lib/utils'
import type { ReactNode } from 'react'

interface SettingsLayoutProps {
  section: SettingsSectionId
  children: ReactNode
}

export function SettingsLayout({ section, children }: SettingsLayoutProps) {
  return (
    <PageLayout className="space-y-4">
      <PageHeader
        title="Settings"
        description="Manage your profile, workspace, team, and preferences."
        className="mb-4"
      />
      <div className="flex flex-col gap-6 lg:flex-row lg:gap-10">
        <SettingsNav active={section} />
        <div className="min-w-0 flex-1">{children}</div>
      </div>
    </PageLayout>
  )
}

function SettingsNav({ active }: { active: SettingsSectionId }) {
  return (
    <nav
      aria-label="Settings"
      className="flex shrink-0 flex-row gap-1 overflow-x-auto lg:w-52 lg:flex-col lg:gap-0.5"
    >
      {SETTINGS_SECTIONS.map((item) => (
        <Link
          key={item.id}
          to="/settings"
          search={{ section: item.id }}
          className={cn(
            'whitespace-nowrap rounded-md px-3 py-2 text-sm transition-colors',
            active === item.id
              ? 'bg-muted font-medium text-foreground'
              : 'text-muted-foreground hover:bg-muted/50 hover:text-foreground',
          )}
        >
          {item.label}
        </Link>
      ))}
    </nav>
  )
}
