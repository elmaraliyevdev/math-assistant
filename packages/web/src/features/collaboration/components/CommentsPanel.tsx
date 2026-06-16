import { useState } from 'react'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { PermissionActionButton } from '@/features/collaboration/components/PermissionActionButton'
import {
  useAddSimulationComment,
  useSimulationComments,
} from '@/features/collaboration/hooks/use-collaboration'
import { RoleBadge } from '@/features/organizations/components/RoleBadge'
import { useOrganizationPermissions } from '@/features/organizations/use-organizations'
import { canRequestReview, PERMISSION_MESSAGES } from '@/lib/permissions'
import type { OrganizationRole } from '@/types/api'
import { formatDate } from '@/lib/utils'

interface CommentsPanelProps {
  simulationId: string
}

export function CommentsPanel({ simulationId }: CommentsPanelProps) {
  const comments = useSimulationComments(simulationId)
  const addComment = useAddSimulationComment(simulationId)
  const { role } = useOrganizationPermissions()
  const canComment = canRequestReview(role)
  const [draft, setDraft] = useState('')

  return (
    <Card>
      <CardHeader>
        <CardTitle>Comments</CardTitle>
        <p className="text-sm text-muted-foreground">
          Discuss mathematics iterations with your team.
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Textarea
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder="Add a comment for reviewers…"
            rows={3}
            disabled={!canComment}
          />
          <PermissionActionButton
            allowed={canComment}
            disabledReason={PERMISSION_MESSAGES.requestReview}
            onClick={() => {
              const content = draft.trim()
              if (!content) return
              addComment.mutate(content, { onSuccess: () => setDraft('') })
            }}
            disabled={addComment.isPending || draft.trim().length === 0}
          >
            Add comment
          </PermissionActionButton>
        </div>

        {comments.isLoading && (
          <p className="text-sm text-muted-foreground">Loading comments…</p>
        )}

        <ul className="space-y-3">
          {comments.data?.items.map((comment) => (
            <li key={comment.id} className="rounded-lg border p-3">
              <div className="flex flex-wrap items-center gap-2">
                <p className="text-sm font-medium">
                  {comment.authorName ?? comment.authorEmail ?? comment.userId}
                </p>
                {comment.authorRole && (
                  <RoleBadge role={comment.authorRole as OrganizationRole} />
                )}
              </div>
              <p className="mt-2 text-sm">{comment.content}</p>
              <p className="mt-2 text-xs text-muted-foreground">
                {formatDate(comment.createdAt)}
              </p>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}
