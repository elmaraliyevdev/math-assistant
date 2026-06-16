import { Info } from 'lucide-react'

interface PermissionNoticeProps {
  message: string
}

export function PermissionNotice({ message }: PermissionNoticeProps) {
  return (
    <div className="flex items-start gap-2 rounded-md border border-dashed bg-muted/40 p-3 text-sm text-muted-foreground">
      <Info className="mt-0.5 h-4 w-4 shrink-0" />
      <p>{message}</p>
    </div>
  )
}
