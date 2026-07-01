import { useNavigate } from '@tanstack/react-router'
import {
  Building2,
  Check,
  CreditCard,
  Keyboard,
  LifeBuoy,
  LogOut,
  MoreHorizontal,
  Plus,
  Settings,
  User,
} from 'lucide-react'

import { Avatar, AvatarFallback, getInitials } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useLogout, useMe } from '@/features/auth/use-auth'
import { useCurrentOrganization } from '@/hooks/use-sync-organization'
import { useOrganizationStore } from '@/stores/organization-store'
import { cn } from '@/lib/utils'

export function SidebarUserMenu({ className }: { className?: string }) {
  const navigate = useNavigate()
  const logout = useLogout()
  const { data: me } = useMe()
  const currentOrg = useCurrentOrganization()
  const organizations = me?.organizations ?? []
  const currentOrganizationId = useOrganizationStore((state) => state.currentOrganizationId)
  const setCurrentOrganizationId = useOrganizationStore((state) => state.setCurrentOrganizationId)

  const displayName = me?.user.fullName?.trim() || me?.user.email || 'Account'
  const email = me?.user.email ?? ''
  const workspaceName = currentOrg?.organizationName ?? 'Workspace'

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          type="button"
          className={cn(
            'group flex w-full items-center gap-3 rounded-xl border border-border/50 bg-muted/20 p-3 text-left transition-all duration-200',
            'hover:border-border hover:bg-muted/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
            className,
          )}
        >
          <Avatar className="h-9 w-9 transition-transform duration-200 group-hover:scale-[1.02]">
            <AvatarFallback className="bg-primary/10 text-primary">
              {getInitials(displayName)}
            </AvatarFallback>
          </Avatar>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium">{displayName}</p>
            <p className="truncate text-xs text-muted-foreground">{workspaceName}</p>
          </div>
          <MoreHorizontal className="h-4 w-4 shrink-0 text-muted-foreground opacity-70 transition-opacity duration-200 group-hover:opacity-100" />
        </button>
      </DropdownMenuTrigger>

      <DropdownMenuContent side="top" align="start" sideOffset={8} className="w-64">
        <div className="px-2 py-2">
          <div className="flex items-start gap-3">
            <Avatar className="h-10 w-10">
              <AvatarFallback className="bg-primary/10 text-primary">
                {getInitials(displayName)}
              </AvatarFallback>
            </Avatar>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-semibold">{displayName}</p>
              <p className="truncate text-xs text-muted-foreground">{email}</p>
            </div>
          </div>
        </div>

        <DropdownMenuSeparator />

        <DropdownMenuItem className="gap-2" onClick={() => navigate({ to: '/settings' })}>
          <User className="h-4 w-4" />
          Account
        </DropdownMenuItem>

        <DropdownMenuSub>
          <DropdownMenuSubTrigger className="gap-2">
            <Building2 className="h-4 w-4" />
            Workspace
          </DropdownMenuSubTrigger>
          <DropdownMenuSubContent sideOffset={8} className="w-56">
            {organizations.map((org) => {
              const active = org.organizationId === currentOrganizationId
              return (
                <DropdownMenuItem
                  key={org.organizationId}
                  className="gap-2"
                  onClick={() => setCurrentOrganizationId(org.organizationId)}
                >
                  <Check className={cn('h-4 w-4', active ? 'opacity-100' : 'opacity-0')} />
                  <div className="flex min-w-0 flex-col">
                    <span className="truncate">{org.organizationName}</span>
                    <span className="text-xs capitalize text-muted-foreground">{org.role}</span>
                  </div>
                </DropdownMenuItem>
              )
            })}
            <DropdownMenuSeparator />
            <DropdownMenuItem
              className="gap-2"
              onClick={() => navigate({ to: '/settings', search: { section: 'organization' } })}
            >
              <Plus className="h-4 w-4" />
              Create workspace
            </DropdownMenuItem>
          </DropdownMenuSubContent>
        </DropdownMenuSub>

        <DropdownMenuItem className="gap-2" onClick={() => navigate({ to: '/settings' })}>
          <Settings className="h-4 w-4" />
          Settings
        </DropdownMenuItem>

        <DropdownMenuItem disabled className="gap-2">
          <CreditCard className="h-4 w-4" />
          Billing
          <span className="ml-auto text-xs text-muted-foreground">Soon</span>
        </DropdownMenuItem>

        <DropdownMenuSeparator />

        <DropdownMenuItem
          className="gap-2 text-destructive focus:bg-destructive/10 focus:text-destructive"
          onClick={() => logout.mutate()}
        >
          <LogOut className="h-4 w-4" />
          Sign out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export function SidebarHelpLinks({ className }: { className?: string }) {
  return (
    <div className={cn('space-y-0.5', className)}>
      <p className="px-3 pb-1 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
        Need help
      </p>
      <Button variant="ghost" className="h-8 w-full justify-start gap-2.5 px-3 text-sm font-normal" asChild>
        <a href="https://docs.mathstudio.app" target="_blank" rel="noreferrer">
          <LifeBuoy className="h-4 w-4" />
          Documentation
        </a>
      </Button>
      <Button
        variant="ghost"
        className="h-8 w-full justify-start gap-2.5 px-3 text-sm font-normal text-muted-foreground"
        disabled
      >
        <Keyboard className="h-4 w-4" />
        Keyboard shortcuts
        <span className="ml-auto text-[10px] uppercase tracking-wide opacity-60">Soon</span>
      </Button>
    </div>
  )
}
