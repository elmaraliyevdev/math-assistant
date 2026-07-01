import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { RoleSelect } from '@/features/settings/components/RoleSelect'
import { getErrorMessage } from '@/services/api'

const inviteSchema = z.object({
  email: z.email(),
  role: z.enum(['admin', 'developer', 'viewer']),
})

type InviteForm = z.infer<typeof inviteSchema>

interface InviteMemberDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onInvite: (values: InviteForm) => void
  isPending?: boolean
  error?: unknown
}

export function InviteMemberDialog({
  open,
  onOpenChange,
  onInvite,
  isPending,
  error,
}: InviteMemberDialogProps) {
  const form = useForm<InviteForm>({
    resolver: zodResolver(inviteSchema),
    defaultValues: { role: 'developer' },
  })

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Invite team member</DialogTitle>
        </DialogHeader>
        <form
          className="space-y-4"
          onSubmit={form.handleSubmit((values) => {
            onInvite(values)
            form.reset({ email: '', role: values.role })
          })}
        >
          <div className="space-y-1.5">
            <Label htmlFor="invite-email">Email</Label>
            <Input
              id="invite-email"
              type="email"
              placeholder="teammate@company.com"
              {...form.register('email')}
            />
          </div>
          <RoleSelect
            value={form.watch('role')}
            onValueChange={(value) => form.setValue('role', value as InviteForm['role'])}
            allowedRoles={['admin', 'developer', 'viewer']}
          />
          {error ? (
            <p className="text-sm text-destructive">{getErrorMessage(error)}</p>
          ) : null}
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isPending}>
              Send invite
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

export type { InviteForm }
