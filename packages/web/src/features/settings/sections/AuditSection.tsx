import { useState } from 'react'
import { Download, LayoutList, ListTree, Search } from 'lucide-react'

import { EmptyState } from '@/components/design-system'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  AUDIT_ACTIONS,
  auditToneClassName,
  exportAuditCsv,
  exportAuditJson,
  formatAuditActionLabel,
  formatAuditResource,
  formatRelativeTime,
  getAuditActionTone,
} from '@/features/audit/lib/audit-display'
import { useAuditLogs } from '@/features/audit/hooks/use-audit'
import { SettingsSectionHeader } from '@/features/settings/components/settings-primitives'
import { cn } from '@/lib/utils'

type AuditView = 'table' | 'timeline'

export function AuditSection() {
  const [view, setView] = useState<AuditView>('table')
  const [search, setSearch] = useState('')
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

  const items =
    audit.data?.items.filter((entry) => {
      if (!search.trim()) return true
      const haystack = [
        entry.userName,
        entry.userEmail,
        entry.action,
        entry.entityType,
        entry.entityId,
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()
      return haystack.includes(search.toLowerCase())
    }) ?? []

  return (
    <div className="space-y-4">
      <SettingsSectionHeader
        title="Audit log"
        description="Review platform activity across your workspace."
        aiPrompt="Explain this audit entry and what I should investigate"
        actions={
          <div className="flex flex-wrap gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => exportAuditCsv(items)}
              disabled={!items.length}
            >
              <Download className="mr-1.5 h-3.5 w-3.5" />
              Export CSV
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => exportAuditJson(items)}
              disabled={!items.length}
            >
              Export JSON
            </Button>
          </div>
        }
      />

      <div className="flex flex-col gap-2 rounded-lg border border-border/60 p-2 lg:flex-row lg:items-center">
        <div className="relative min-w-[180px] flex-1">
          <Search className="pointer-events-none absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            className="pl-8"
            placeholder="Search activity…"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>
        <Select value={action} onValueChange={setAction}>
          <SelectTrigger className="w-full lg:w-44">
            <SelectValue placeholder="Action" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All actions</SelectItem>
            {AUDIT_ACTIONS.map((entry) => (
              <SelectItem key={entry} value={entry}>
                {formatAuditActionLabel(entry)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Input
          type="date"
          className="w-full lg:w-36"
          value={dateFrom}
          onChange={(event) => setDateFrom(event.target.value)}
          aria-label="From date"
        />
        <Input
          type="date"
          className="w-full lg:w-36"
          value={dateTo}
          onChange={(event) => setDateTo(event.target.value)}
          aria-label="To date"
        />
        <Input
          className="w-full lg:w-40"
          placeholder="User ID"
          value={userId}
          onChange={(event) => setUserId(event.target.value)}
          aria-label="User filter"
        />
        <div className="flex gap-1 lg:ml-auto">
          <Button
            variant={view === 'table' ? 'secondary' : 'ghost'}
            size="sm"
            onClick={() => setView('table')}
            aria-label="Table view"
          >
            <LayoutList className="h-4 w-4" />
          </Button>
          <Button
            variant={view === 'timeline' ? 'secondary' : 'ghost'}
            size="sm"
            onClick={() => setView('timeline')}
            aria-label="Timeline view"
          >
            <ListTree className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {audit.isLoading ? <Skeleton className="h-48 w-full" /> : null}

      {!audit.isLoading && items.length === 0 ? (
        <EmptyState
          title="No activity recorded"
          description="Workspace actions will appear here as your team creates games and runs simulations."
        />
      ) : null}

      {!audit.isLoading && items.length > 0 && view === 'table' ? (
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>User</TableHead>
                <TableHead>Action</TableHead>
                <TableHead>Resource</TableHead>
                <TableHead>Time</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {items.map((entry) => {
                const tone = getAuditActionTone(entry.action)
                return (
                  <TableRow key={entry.id}>
                    <TableCell>
                      <p className="text-sm font-medium">
                        {entry.userName ?? entry.userEmail ?? 'System'}
                      </p>
                    </TableCell>
                    <TableCell>
                      <span className={auditToneClassName(tone)}>
                        {formatAuditActionLabel(entry.action)}
                      </span>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {formatAuditResource(entry)}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {formatRelativeTime(entry.createdAt)}
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </div>
      ) : null}

      {!audit.isLoading && items.length > 0 && view === 'timeline' ? (
        <div className="space-y-0 border-l border-border/60 pl-4">
          {items.map((entry) => {
            const tone = getAuditActionTone(entry.action)
            const time = new Date(entry.createdAt).toLocaleTimeString(undefined, {
              hour: '2-digit',
              minute: '2-digit',
            })
            return (
              <div key={entry.id} className="relative pb-5 pl-4">
                <span className="absolute -left-[5px] top-1.5 h-2.5 w-2.5 rounded-full bg-primary" />
                <p className="text-xs font-medium text-muted-foreground">{time}</p>
                <p className="text-sm font-medium">{formatAuditActionLabel(entry.action)}</p>
                <p className="text-sm text-muted-foreground">
                  {entry.userName ?? entry.userEmail ?? 'System'} ·{' '}
                  {formatAuditResource(entry)}
                </p>
                <span className={cn('mt-1 inline-flex', auditToneClassName(tone))}>
                  {tone}
                </span>
              </div>
            )
          })}
        </div>
      ) : null}
    </div>
  )
}
