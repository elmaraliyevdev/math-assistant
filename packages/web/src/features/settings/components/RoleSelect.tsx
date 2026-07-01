import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { OrganizationRole } from '@/types/api'

export const ROLE_DEFINITIONS: Record<
  Exclude<OrganizationRole, 'owner'>,
  { label: string; description: string }
> = {
  admin: {
    label: 'Administrator',
    description: 'Manage workspace settings, members, and integrations.',
  },
  developer: {
    label: 'Developer',
    description: 'Create games, run simulations, and edit mathematics.',
  },
  viewer: {
    label: 'Viewer',
    description: 'View games, simulations, and certification reports.',
  },
}

const OWNER_DEFINITION = {
  label: 'Owner',
  description: 'Full control including billing and ownership transfer.',
}

interface RoleSelectProps {
  value: OrganizationRole
  onValueChange: (value: OrganizationRole) => void
  allowedRoles?: Array<Exclude<OrganizationRole, 'owner'>>
  disabled?: boolean
}

export function RoleSelect({
  value,
  onValueChange,
  allowedRoles = ['admin', 'developer', 'viewer'],
  disabled,
}: RoleSelectProps) {
  const selected =
    value === 'owner' ? OWNER_DEFINITION : ROLE_DEFINITIONS[value as keyof typeof ROLE_DEFINITIONS]

  return (
    <div className="space-y-2">
      <Select value={value} onValueChange={(next) => onValueChange(next as OrganizationRole)} disabled={disabled}>
        <SelectTrigger>
          <SelectValue placeholder="Select role" />
        </SelectTrigger>
        <SelectContent>
          {allowedRoles.map((role) => (
            <SelectItem key={role} value={role}>
              {ROLE_DEFINITIONS[role].label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {selected ? (
        <p className="text-xs text-muted-foreground">{selected.description}</p>
      ) : null}
    </div>
  )
}

export function getRoleLabel(role: OrganizationRole): string {
  if (role === 'owner') return OWNER_DEFINITION.label
  return ROLE_DEFINITIONS[role].label
}
