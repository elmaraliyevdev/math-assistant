import { Save } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { DuplicateVersionNotice } from '@/features/games/components/DuplicateVersionNotice'
import { ValidationFindingsTable } from '@/features/games/components/ValidationFindingsTable'
import { getDuplicateVersionDetails } from '@/features/games/hooks/use-games'
import { useReelStudio } from '@/features/reel-studio/context/reel-studio-context'
import { useReelStudioSave } from '@/features/reel-studio/hooks/use-reel-studio-save'
import { getApiErrorCode } from '@/lib/api-error'
import { getValidationFindings } from '@/lib/api-error'

export function ReelStudioToolbar({ gameId }: { gameId: string }) {
  const { document } = useReelStudio()
  const save = useReelStudioSave(gameId)

  const validationFindings =
    save.isError && getApiErrorCode(save.error) === 'VALIDATION_FAILED'
      ? getValidationFindings(save.error)
      : []
  const duplicateDetails = save.isError ? getDuplicateVersionDetails(save.error) : null

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button disabled={save.isPending} onClick={() => save.mutate(document)}>
          <Save className="h-4 w-4" />
          {save.isPending ? 'Saving…' : 'Save as new version'}
        </Button>
      </div>
      {duplicateDetails && (
        <DuplicateVersionNotice details={duplicateDetails} onCancel={() => save.reset()} />
      )}
      {validationFindings.length > 0 && (
        <ValidationFindingsTable findings={validationFindings} />
      )}
    </div>
  )
}
