import { Building2, ChevronDown, Moon, Sun } from 'lucide-react'

import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useMe } from '@/features/auth/use-auth'
import { useOrganizationStore } from '@/stores/organization-store'
import { useThemeStore } from '@/stores/theme-store'

export function OrganizationSwitcher() {
  const { data: me } = useMe()
  const currentOrganizationId = useOrganizationStore(
    (state) => state.currentOrganizationId,
  )
  const setCurrentOrganizationId = useOrganizationStore(
    (state) => state.setCurrentOrganizationId,
  )

  const organizations = me?.organizations ?? []
  const current =
    organizations.find((org) => org.organizationId === currentOrganizationId) ??
    organizations[0]

  if (!current) {
    return null
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="max-w-[240px] justify-between">
          <span className="flex items-center gap-2 truncate">
            <Building2 className="h-4 w-4" />
            {current.organizationName}
          </span>
          <ChevronDown className="h-4 w-4 opacity-60" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        {organizations.map((org) => (
          <DropdownMenuItem
            key={org.organizationId}
            onClick={() => setCurrentOrganizationId(org.organizationId)}
          >
            <div className="flex flex-col">
              <span>{org.organizationName}</span>
              <span className="text-xs text-muted-foreground capitalize">
                {org.role}
              </span>
            </div>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export function ThemeToggle() {
  const theme = useThemeStore((state) => state.theme)
  const toggle = useThemeStore((state) => state.toggle)

  return (
    <Button variant="ghost" size="icon" onClick={toggle} aria-label="Toggle theme">
      {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
    </Button>
  )
}
