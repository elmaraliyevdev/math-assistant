import { Braces } from 'lucide-react'
import { useState } from 'react'

import { Button } from '@/components/ui/button'
import { JsonViewer } from '@/features/games/components/JsonViewer'
import { useReelStudioPreview } from '@/features/reel-studio/context/reel-studio-context'

export function JsonPreviewDrawer() {
  const previewJson = useReelStudioPreview()
  const [open, setOpen] = useState(false)

  return (
    <>
      <Button type="button" variant="outline" onClick={() => setOpen((value) => !value)}>
        <Braces className="h-4 w-4" />
        {open ? 'Hide JSON preview' : 'JSON preview'}
      </Button>
      {open && (
        <div className="fixed inset-y-0 right-0 z-40 w-full max-w-xl border-l bg-background p-4 shadow-xl">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-lg font-semibold">Canonical JSON preview</h3>
            <Button type="button" variant="ghost" size="sm" onClick={() => setOpen(false)}>
              Close
            </Button>
          </div>
          <div className="h-[calc(100vh-6rem)] overflow-auto">
            <JsonViewer value={previewJson} />
          </div>
        </div>
      )}
    </>
  )
}
