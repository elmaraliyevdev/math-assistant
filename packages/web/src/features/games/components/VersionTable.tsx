import { Link } from '@tanstack/react-router'
import { Eye } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { CopyHashButton } from '@/features/games/components/GameTable'
import type { GameVersionSummary } from '@/types/api'
import { formatDate } from '@/lib/utils'

interface VersionTableProps {
  gameId: string
  versions: GameVersionSummary[]
  loading?: boolean
  onViewJson: (version: GameVersionSummary) => void
  onUploadJson?: () => void
  onUseTemplate?: () => void
}

export function VersionTable({
  gameId,
  versions,
  loading,
  onViewJson,
  onUploadJson,
  onUseTemplate,
}: VersionTableProps) {
  if (loading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 3 }).map((_, index) => (
          <Skeleton key={index} className="h-12 w-full" />
        ))}
      </div>
    )
  }

  if (versions.length === 0) {
    return (
      <div className="rounded-lg border border-dashed p-8 text-center">
        <p className="text-sm text-muted-foreground">No versions uploaded.</p>
        <p className="mt-2 text-sm text-muted-foreground">To start:</p>
        <div className="mt-4 flex flex-wrap justify-center gap-2">
          {onUploadJson && (
            <Button onClick={onUploadJson}>Upload JSON</Button>
          )}
          {onUseTemplate && (
            <Button variant="outline" onClick={onUseTemplate}>
              Use Template
            </Button>
          )}
        </div>
      </div>
    )
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Version</TableHead>
          <TableHead>Content hash</TableHead>
          <TableHead>Engine</TableHead>
          <TableHead>Created</TableHead>
          <TableHead className="text-right">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {versions.map((version) => (
          <TableRow key={version.id}>
            <TableCell>
              <Badge variant="secondary">v{version.version}</Badge>
            </TableCell>
            <TableCell className="font-mono text-xs">
              {version.contentHash.slice(0, 16)}…
            </TableCell>
            <TableCell>{version.engineVersion}</TableCell>
            <TableCell>{formatDate(version.createdAt)}</TableCell>
            <TableCell>
              <div className="flex justify-end gap-1">
                <CopyHashButton hash={version.contentHash} />
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onViewJson(version)}
                >
                  JSON
                </Button>
                <Button variant="ghost" size="icon" asChild>
                  <Link
                    to="/games/$gameId/versions/$versionId"
                    params={{ gameId, versionId: version.id }}
                  >
                    <Eye className="h-4 w-4" />
                    <span className="sr-only">View version</span>
                  </Link>
                </Button>
              </div>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
