import { FileText } from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useOptimizerStudio } from '@/features/reel-studio/optimizer/context/optimizer-context'

export function ProposalDetailPanel() {
  const { previewProposal } = useOptimizerStudio()
  if (!previewProposal) {
    return null
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm">
          <FileText className="h-4 w-4" />
          Proposal detail
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 text-sm">
        <p className="font-medium">{previewProposal.title}</p>
        <p className="text-xs text-muted-foreground">{previewProposal.description}</p>
        <div className="rounded-md border bg-muted/30 p-3 text-xs">
          <p className="font-medium">Why it exists</p>
          <p className="mt-1">{previewProposal.reason}</p>
          <p className="mt-2 font-medium">Expected impact</p>
          <ul className="mt-1 space-y-0.5">
            {previewProposal.expectedImprovement.map((item) => (
              <li key={item}>✔ {item}</li>
            ))}
          </ul>
          <p className="mt-2">
            Affected reels: {previewProposal.affectedReels.map((reel) => reel + 1).join(', ')}
          </p>
          <p>Affected symbols: {previewProposal.affectedSymbols.join(', ')}</p>
          <p>
            Confidence {previewProposal.confidence}% · Risk {previewProposal.estimatedRisk}
          </p>
        </div>
      </CardContent>
    </Card>
  )
}

export function OptimizationReportPanel() {
  const { lastReport } = useOptimizerStudio()
  if (!lastReport) {
    return null
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">Optimization report</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-2 gap-2 text-xs">
        <span className="text-muted-foreground">Current health</span>
        <span>{lastReport.currentHealth}</span>
        <span className="text-muted-foreground">New health</span>
        <span>{lastReport.newHealth}</span>
        <span className="text-muted-foreground">Improvement</span>
        <span>+{lastReport.improvement}</span>
        <span className="text-muted-foreground">Applied</span>
        <span>{lastReport.appliedProposals.length}</span>
        <span className="text-muted-foreground">Rejected</span>
        <span>{lastReport.rejectedProposals.length}</span>
        <span className="text-muted-foreground">Next estimate</span>
        <span>+{lastReport.estimatedNextImprovement}</span>
        <span className="text-muted-foreground">Time</span>
        <span>{lastReport.timeSpentMs} ms</span>
      </CardContent>
    </Card>
  )
}

export function GoalEvaluationPanel() {
  const { output } = useOptimizerStudio()

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">Goal evaluation</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {output.goalEvaluation.map((goal) => (
          <div key={goal.goalId} className="flex items-center justify-between text-xs">
            <span>
              {goal.status === 'pass' ? '✔' : goal.status === 'warning' ? '⚠' : '✖'} {goal.label}
            </span>
            <span className="text-muted-foreground">
              {goal.current} / {goal.target}
            </span>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
