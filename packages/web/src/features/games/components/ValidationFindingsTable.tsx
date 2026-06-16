import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import type { ValidationFinding } from '@/features/games/types'

interface ValidationFindingsTableProps {
  findings: ValidationFinding[]
  emptyMessage?: string
}

function severityVariant(severity: string) {
  switch (severity.toLowerCase()) {
    case 'error':
      return 'danger' as const
    case 'warning':
      return 'warning' as const
    default:
      return 'secondary' as const
  }
}

export function ValidationFindingsTable({
  findings,
  emptyMessage = 'No validation findings.',
}: ValidationFindingsTableProps) {
  if (findings.length === 0) {
    return <p className="text-sm text-muted-foreground">{emptyMessage}</p>
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Code</TableHead>
          <TableHead>Severity</TableHead>
          <TableHead>Message</TableHead>
          <TableHead>Location</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {findings.map((finding, index) => (
          <TableRow key={`${finding.code}-${finding.path}-${index}`}>
            <TableCell className="font-mono text-xs">{finding.code}</TableCell>
            <TableCell>
              <Badge variant={severityVariant(finding.severity)}>
                {finding.severity}
              </Badge>
            </TableCell>
            <TableCell>{finding.message}</TableCell>
            <TableCell className="font-mono text-xs">{finding.path || '—'}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
