import { FileBarChart } from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useGeneratorStudio } from '@/features/reel-studio/generator/context/generator-context'

export function GenerationReportPanel() {
  const { report } = useGeneratorStudio()

  if (!report) {
    return null
  }

  const top = report.candidates[0]

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm">
          <FileBarChart className="h-4 w-4" />
          Generation report
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 text-sm">
        <div className="grid grid-cols-2 gap-2 text-xs">
          <span className="text-muted-foreground">Generation time</span>
          <span>{report.generationTimeMs.toFixed(1)} ms</span>
          <span className="text-muted-foreground">Seed</span>
          <span>{report.seed}</span>
          {top ? (
            <>
              <span className="text-muted-foreground">Quality score</span>
              <span>{top.qualityScore}</span>
              <span className="text-muted-foreground">Repair count</span>
              <span>{top.repairCount}</span>
              <span className="text-muted-foreground">Warnings</span>
              <span>{top.warnings}</span>
            </>
          ) : null}
        </div>
        <div className="pt-2">
          <p className="text-xs font-medium text-muted-foreground">Candidate ranking</p>
          <ol className="mt-1 list-decimal space-y-1 pl-4 text-xs">
            {report.ranking.map((id) => {
              const candidate = report.candidates.find((item) => item.id === id)
              return (
                <li key={id}>
                  {candidate ? `Score ${candidate.qualityScore} — ${candidate.summary}` : id}
                </li>
              )
            })}
          </ol>
        </div>
      </CardContent>
    </Card>
  )
}
