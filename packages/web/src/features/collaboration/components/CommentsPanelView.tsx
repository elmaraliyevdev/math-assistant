import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { RoleBadge } from '@/features/organizations/components/RoleBadge'
import type { SimulationComment } from '@/features/collaboration/types'
import type { OrganizationRole } from '@/types/api'
import { formatDate } from '@/lib/utils'

export function CommentsPanelView({
  comments,
  readOnly = true,
}: {
  comments: SimulationComment[]
  readOnly?: boolean
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Comments</CardTitle>
        <p className="text-sm text-muted-foreground">
          Discuss mathematics iterations with your team.
        </p>
      </CardHeader>
      <CardContent className="space-y-3">
        {!readOnly ? null : null}
        <ul className="space-y-3">
          {comments.map((comment) => (
            <li key={comment.id} className="rounded-lg border p-3">
              <div className="flex flex-wrap items-center gap-2">
                <p className="text-sm font-medium">
                  {comment.authorName ?? comment.authorEmail ?? comment.userId}
                </p>
                {comment.authorRole ? (
                  <RoleBadge role={comment.authorRole as OrganizationRole} />
                ) : null}
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
