import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { CertificationReadinessSummary } from '@/types/api'

interface CertificationReadinessPanelProps {
  readiness: CertificationReadinessSummary
}

export function CertificationReadinessPanel({
  readiness,
}: CertificationReadinessPanelProps) {
  const statusVariant =
    readiness.certificationStatus === 'certification_blocked'
      ? 'danger'
      : readiness.certificationStatus === 'cleared'
        ? 'success'
        : 'warning'

  return (
    <Card>
      <CardHeader>
        <CardTitle>Certification Readiness</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant={statusVariant}>
            {readiness.certificationStatus.replaceAll('_', ' ')}
          </Badge>
          <span className="text-sm text-muted-foreground">
            Estimated iterations remaining: {readiness.estimatedIterationsRemaining}
          </span>
        </div>

        {readiness.blockingIssues.length > 0 && (
          <div className="space-y-2">
            <p className="text-sm font-medium">Blocking issues</p>
            <ul className="list-disc space-y-1 pl-5 text-sm text-muted-foreground">
              {readiness.blockingIssues.map((issue) => (
                <li key={issue}>{issue}</li>
              ))}
            </ul>
          </div>
        )}

        {readiness.requiredActions.length > 0 && (
          <div className="space-y-2">
            <p className="text-sm font-medium">Required actions</p>
            <ol className="list-decimal space-y-1 pl-5 text-sm text-muted-foreground">
              {readiness.requiredActions.map((action) => (
                <li key={action}>{action}</li>
              ))}
            </ol>
          </div>
        )}

        {readiness.blockingIssues.length === 0 &&
          readiness.requiredActions.length === 0 && (
            <p className="text-sm text-muted-foreground">
              No blocking issues identified. Mathematics are ready for certification review.
            </p>
          )}
      </CardContent>
    </Card>
  )
}
