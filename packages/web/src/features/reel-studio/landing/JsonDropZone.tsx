import { useCallback, useState } from 'react'
import { FileJson, Upload } from 'lucide-react'

import { cn } from '@/lib/utils'

export function JsonDropZone({ className }: { className?: string }) {
  const [dragging, setDragging] = useState(false)

  const onDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    setDragging(false)
    const file = event.dataTransfer.files[0]
    if (!file || !file.name.endsWith('.json')) return
    const reader = new FileReader()
    reader.onload = () => {
      try {
        const parsed = JSON.parse(String(reader.result))
        sessionStorage.setItem('ma_import_canonical_json', JSON.stringify(parsed))
        window.location.href = '/games/create'
      } catch {
        /* invalid json */
      }
    }
    reader.readAsText(file)
  }, [])

  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center rounded-lg border border-dashed px-6 py-8 text-center transition-colors',
        dragging ? 'border-primary bg-primary/5' : 'border-border/60 bg-muted/20',
        className,
      )}
      onDragOver={(event) => {
        event.preventDefault()
        setDragging(true)
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={onDrop}
    >
      <Upload className="mb-2 h-8 w-8 text-muted-foreground" />
      <p className="text-sm font-medium">Drag & drop canonical JSON</p>
      <p className="mt-1 text-xs text-muted-foreground">
        We&apos;ll open the game creator with your file loaded.
      </p>
      <FileJson className="mt-3 h-4 w-4 text-muted-foreground/60" />
    </div>
  )
}
