import { Check } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { useGeneratorStudio } from '@/features/reel-studio/generator/context/generator-context'
import { cn } from '@/lib/utils'

export function CandidateComparisonContent() {
  const {
    report,
    selectedCandidateId,
    previewCandidate,
    selectCandidate,
    applyCandidate,
    clearPreview,
  } = useGeneratorStudio()

  if (!report) return null

  return (
    <div className="space-y-2">
      {report.candidates.map((candidate, index) => {
        const label = String.fromCharCode(65 + index)
        const selected = candidate.id === selectedCandidateId
        return (
          <button
            key={candidate.id}
            type="button"
            onClick={() => selectCandidate(candidate.id)}
            className={cn(
              'w-full rounded-lg p-4 text-left transition-colors duration-150',
              selected ? 'bg-primary/10 ring-1 ring-primary/30' : 'bg-muted/30 hover:bg-muted/50',
            )}
          >
            <div className="flex items-center justify-between gap-2">
              <p className="text-sm font-medium">Candidate {label}</p>
              <Badge variant={candidate.violations === 0 ? 'secondary' : 'danger'}>
                Score {candidate.qualityScore}
              </Badge>
            </div>
            <p className="mt-2 text-xs text-muted-foreground">{candidate.summary}</p>
            <p className="mt-1 text-xs text-muted-foreground">
              {candidate.violations} violations · {candidate.warnings} warnings ·{' '}
              {candidate.repairCount} repairs
            </p>
          </button>
        )
      })}

      {previewCandidate ? (
        <div className="flex flex-wrap gap-2 pt-2">
          <Button type="button" size="sm" onClick={applyCandidate}>
            <Check className="h-4 w-4" />
            Apply candidate
          </Button>
          <Button type="button" size="sm" variant="outline" onClick={clearPreview}>
            Dismiss
          </Button>
        </div>
      ) : null}
    </div>
  )
}

/** @deprecated Use CandidateComparisonContent inside DesignInspector accordion */
export function CandidateComparisonPanel() {
  return <CandidateComparisonContent />
}
