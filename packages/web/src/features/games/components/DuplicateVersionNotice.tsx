import { useNavigate } from '@tanstack/react-router'

import { Button } from '@/components/ui/button'
import type { DuplicateVersionDetails } from '@/features/games/hooks/use-games'

interface DuplicateVersionNoticeProps {
  details: DuplicateVersionDetails
  onCancel: () => void
}

export function DuplicateVersionNotice({
  details,
  onCancel,
}: DuplicateVersionNoticeProps) {
  const navigate = useNavigate()

  return (
    <div className="space-y-3 rounded-lg border border-amber-500/30 bg-amber-500/5 p-4">
      <p className="text-sm font-medium text-amber-800 dark:text-amber-200">
        This version already exists in your organization.
      </p>
      <p className="text-sm text-muted-foreground">
        {details.existingGameName} · {details.existingVersionName}
      </p>
      <div className="flex flex-wrap gap-2">
        <Button
          type="button"
          onClick={() => {
            void navigate({
              to: '/games/$gameId/versions/$versionId',
              params: {
                gameId: details.existingGameId,
                versionId: details.existingVersionId,
              },
            })
            onCancel()
          }}
        >
          Open existing version
        </Button>
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel upload
        </Button>
      </div>
    </div>
  )
}
