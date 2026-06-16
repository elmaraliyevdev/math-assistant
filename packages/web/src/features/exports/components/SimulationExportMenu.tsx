import { Download } from 'lucide-react'
import { useState } from 'react'

import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { exportsApi } from '@/services/exports'
import { toast } from '@/lib/toast'

export function SimulationExportMenu({
  simulationId,
  disabled = false,
}: {
  simulationId: string
  disabled?: boolean
}) {
  const [format, setFormat] = useState<'json' | 'csv' | 'pdf'>('json')
  const [loading, setLoading] = useState(false)

  return (
    <div className="flex items-center gap-2">
      <Select
        value={format}
        onValueChange={(value) => setFormat(value as 'json' | 'csv' | 'pdf')}
      >
        <SelectTrigger className="w-28">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="json">JSON</SelectItem>
          <SelectItem value="csv">CSV</SelectItem>
          <SelectItem value="pdf">PDF</SelectItem>
        </SelectContent>
      </Select>
      <Button
        variant="outline"
        disabled={disabled || loading}
        onClick={async () => {
          setLoading(true)
          try {
            await exportsApi.downloadSimulation(simulationId, format)
            toast.success(`Exported as ${format.toUpperCase()}`)
          } catch {
            toast.error('Export failed')
          } finally {
            setLoading(false)
          }
        }}
      >
        <Download className="h-4 w-4" />
        Export
      </Button>
    </div>
  )
}
