import { Download, Upload } from 'lucide-react'
import { useRef } from 'react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useConstraintStudio } from '@/features/reel-studio/constraints/context/constraint-studio-context'

export function ConstraintPresetManager() {
  const {
    constraintDocument,
    listPresets,
    loadPreset,
    saveCustomPreset,
    exportCustomPreset,
    importCustomPreset,
    setEdgeWrapping,
  } = useConstraintStudio()
  const fileRef = useRef<HTMLInputElement>(null)
  const presets = listPresets()

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">Constraint presets</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <Select
          value={constraintDocument.activePresetId ?? 'none'}
          onValueChange={(value) => {
            if (value !== 'none') {
              loadPreset(value)
            }
          }}
        >
          <SelectTrigger className="h-8 text-xs">
            <SelectValue placeholder="Load preset" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none">Select preset…</SelectItem>
            {presets.map((preset) => (
              <SelectItem key={preset.id} value={preset.id}>
                {preset.name}
                {preset.builtIn ? ' (built-in)' : ''}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <label className="flex items-center gap-2 text-xs">
          <input
            type="checkbox"
            checked={constraintDocument.edgeWrapping}
            onChange={(event) => setEdgeWrapping(event.target.checked)}
          />
          Edge wrapping (circular reels)
        </label>
        <div className="flex flex-wrap gap-2">
          <Input
            className="h-8 flex-1 text-xs"
            placeholder="Preset name"
            id="preset-name"
          />
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={() => {
              const input = document.getElementById('preset-name') as HTMLInputElement | null
              if (input?.value) {
                saveCustomPreset(input.value)
                input.value = ''
              }
            }}
          >
            Save
          </Button>
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={() => {
              const id = constraintDocument.activePresetId
              if (!id) {
                return
              }
              const blob = new Blob([exportCustomPreset(id)], { type: 'application/json' })
              const url = URL.createObjectURL(blob)
              const anchor = document.createElement('a')
              anchor.href = url
              anchor.download = `${id}.json`
              anchor.click()
              URL.revokeObjectURL(url)
            }}
          >
            <Download className="h-3.5 w-3.5" />
          </Button>
          <Button type="button" size="sm" variant="outline" onClick={() => fileRef.current?.click()}>
            <Upload className="h-3.5 w-3.5" />
          </Button>
          <input
            ref={fileRef}
            type="file"
            accept="application/json"
            className="hidden"
            onChange={async (event) => {
              const file = event.target.files?.[0]
              if (!file) {
                return
              }
              importCustomPreset(await file.text())
              event.target.value = ''
            }}
          />
        </div>
      </CardContent>
    </Card>
  )
}
