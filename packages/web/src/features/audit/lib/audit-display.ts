import type { AuditLog } from '@/services/audit'
import { cn } from '@/lib/utils'

export type AuditActionTone =
  | 'create'
  | 'delete'
  | 'update'
  | 'invite'
  | 'approve'
  | 'run'
  | 'failed'
  | 'auth'
  | 'default'

const TONE_STYLES: Record<AuditActionTone, string> = {
  create: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200',
  delete: 'bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-200',
  update: 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-200',
  invite: 'bg-violet-100 text-violet-800 dark:bg-violet-950 dark:text-violet-200',
  approve: 'bg-teal-100 text-teal-800 dark:bg-teal-950 dark:text-teal-200',
  run: 'bg-amber-100 text-amber-900 dark:bg-amber-950 dark:text-amber-100',
  failed: 'bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-200',
  auth: 'bg-slate-100 text-slate-800 dark:bg-slate-900 dark:text-slate-200',
  default: 'bg-muted text-muted-foreground',
}

export function getAuditActionTone(action: string): AuditActionTone {
  if (action.includes('fail') || action.includes('error')) return 'failed'
  if (action.startsWith('auth.')) return 'auth'
  if (action.includes('.create') || action.includes('.add')) return 'create'
  if (action.includes('.delete') || action.includes('.remove')) return 'delete'
  if (action.includes('.update') || action.includes('.edit')) return 'update'
  if (action.includes('invite')) return 'invite'
  if (action.includes('approve')) return 'approve'
  if (action.includes('simulation') || action.includes('run')) return 'run'
  return 'default'
}

export function formatAuditActionLabel(action: string): string {
  const parts = action.split('.')
  const verb = parts[parts.length - 1] ?? action
  const resource = parts.slice(0, -1).join(' ')
  const label = verb.replace(/_/g, ' ')
  if (!resource) return label
  return `${label} ${resource}`.replace(/\b\w/g, (char) => char.toUpperCase())
}

export function formatAuditResource(entry: AuditLog): string {
  const label = entry.entityType.replace(/_/g, ' ')
  if (!entry.entityId) return label
  const shortId = entry.entityId.length > 12 ? `${entry.entityId.slice(0, 8)}…` : entry.entityId
  return `${label} #${shortId}`
}

export function auditToneClassName(tone: AuditActionTone): string {
  return cn('inline-flex rounded-md px-2 py-0.5 text-xs font-medium capitalize', TONE_STYLES[tone])
}

export const AUDIT_ACTIONS = [
  'auth.login',
  'auth.logout',
  'game.create',
  'game.delete',
  'game_version.create',
  'simulation.create',
  'organization.member.add',
  'organization.member.remove',
] as const

export function exportAuditCsv(items: AuditLog[]) {
  const header = ['User', 'Email', 'Action', 'Resource', 'Entity ID', 'Timestamp']
  const rows = items.map((entry) => [
    entry.userName ?? 'System',
    entry.userEmail ?? '',
    entry.action,
    entry.entityType,
    entry.entityId ?? '',
    entry.createdAt,
  ])
  const csv = [header, ...rows]
    .map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(','))
    .join('\n')
  downloadText(csv, 'audit-log.csv', 'text/csv')
}

export function exportAuditJson(items: AuditLog[]) {
  downloadText(JSON.stringify(items, null, 2), 'audit-log.json', 'application/json')
}

function downloadText(content: string, filename: string, type: string) {
  const blob = new Blob([content], { type })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  anchor.click()
  URL.revokeObjectURL(url)
}

export function formatRelativeTime(value: string): string {
  const date = new Date(value)
  const diffMs = Date.now() - date.getTime()
  const minutes = Math.floor(diffMs / 60_000)
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes} minute${minutes === 1 ? '' : 's'} ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours} hour${hours === 1 ? '' : 's'} ago`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days} day${days === 1 ? '' : 's'} ago`
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
}
