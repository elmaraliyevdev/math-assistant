import { useState } from 'react'

import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Textarea } from '@/components/ui/textarea'

interface ReviewDecisionDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  title: string
  description: string
  confirmLabel: string
  requireReason?: boolean
  onConfirm: (reason?: string) => void
  pending?: boolean
}

export function ReviewDecisionDialog({
  open,
  onOpenChange,
  title,
  description,
  confirmLabel,
  requireReason = false,
  onConfirm,
  pending = false,
}: ReviewDecisionDialogProps) {
  const [reason, setReason] = useState('')

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>{description}</DialogDescription>
        </DialogHeader>
        {requireReason && (
          <Textarea
            value={reason}
            onChange={(event) => setReason(event.target.value)}
            placeholder="Explain what needs to change…"
            rows={4}
          />
        )}
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            onClick={() => {
              onConfirm(requireReason ? reason.trim() : undefined)
              setReason('')
            }}
            disabled={pending || (requireReason && reason.trim().length === 0)}
          >
            {confirmLabel}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
