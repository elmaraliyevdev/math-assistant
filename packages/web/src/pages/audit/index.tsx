import { useState } from 'react'

import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Skeleton } from '@/components/ui/skeleton'
import { useAuditLogs } from '@/features/audit/hooks/use-audit'
import { formatDate } from '@/lib/utils'

const ACTIONS = [
  'auth.login',
  'auth.logout',
  'game.create',
  'game.delete',
  'game_version.create',
  'simulation.create',
  'organization.member.add',
  'organization.member.remove',
] as const

export function AuditPage() {
  const [action, setAction] = useState('all')
  const [userId, setUserId] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')

  const audit = useAuditLogs({
    page: 1,
    pageSize: 50,
    action: action === 'all' ? undefined : action,
    userId: userId || undefined,
    dateFrom: dateFrom || undefined,
    dateTo: dateTo || undefined,
  })

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Audit log</h2>
        <p className="text-muted-foreground">
          Review platform activity across your organizations.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <div className="space-y-2">
          <Label htmlFor="audit-user">User ID</Label>
          <Input
            id="audit-user"
            placeholder="Filter by user"
            value={userId}
            onChange={(event) => setUserId(event.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label>Action</Label>
          <Select value={action} onValueChange={setAction}>
            <SelectTrigger>
              <SelectValue placeholder="All actions" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All actions</SelectItem>
              {ACTIONS.map((entry) => (
                <SelectItem key={entry} value={entry}>
                  {entry}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label htmlFor="audit-from">From</Label>
          <Input
            id="audit-from"
            type="date"
            value={dateFrom}
            onChange={(event) => setDateFrom(event.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="audit-to">To</Label>
          <Input
            id="audit-to"
            type="date"
            value={dateTo}
            onChange={(event) => setDateTo(event.target.value)}
          />
        </div>
      </div>

      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>User</TableHead>
              <TableHead>Action</TableHead>
              <TableHead>Entity</TableHead>
              <TableHead>Timestamp</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {audit.isLoading &&
              Array.from({ length: 4 }).map((_, index) => (
                <TableRow key={index}>
                  <TableCell colSpan={4}>
                    <Skeleton className="h-8 w-full" />
                  </TableCell>
                </TableRow>
              ))}
            {audit.data?.items.map((entry) => (
              <TableRow key={entry.id}>
                <TableCell>
                  <p className="font-medium">
                    {entry.userName ?? entry.userEmail ?? 'System'}
                  </p>
                  {entry.userEmail && (
                    <p className="text-xs text-muted-foreground">
                      {entry.userEmail}
                    </p>
                  )}
                </TableCell>
                <TableCell>{entry.action}</TableCell>
                <TableCell>
                  {entry.entityType}
                  {entry.entityId ? ` · ${entry.entityId}` : ''}
                </TableCell>
                <TableCell>{formatDate(entry.createdAt)}</TableCell>
              </TableRow>
            ))}
            {!audit.isLoading && (audit.data?.items.length ?? 0) === 0 && (
              <TableRow>
                <TableCell colSpan={4} className="text-muted-foreground">
                  No audit entries found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
