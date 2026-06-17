import { zodResolver } from '@hookform/resolvers/zod'
import { FileJson, Upload } from 'lucide-react'
import { useRef, useState } from 'react'
import { useForm } from 'react-hook-form'

import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { TemplateSelector } from '@/features/game-templates/components/TemplateSelector'
import { useGameTemplates } from '@/features/game-templates/hooks/use-game-templates'
import type { GameTemplate, VersionUploadTab } from '@/features/game-templates/types'
import { DuplicateVersionNotice } from '@/features/games/components/DuplicateVersionNotice'
import { ValidationFindingsTable } from '@/features/games/components/ValidationFindingsTable'
import {
  DEFAULT_ENGINE_VERSION,
  parseCanonicalJson,
  versionUploadSchema,
  type VersionUploadFormValues,
} from '@/features/games/schemas/game-schemas'
import {
  getDuplicateVersionDetails,
  useCreateGameVersion,
} from '@/features/games/hooks/use-games'
import { getApiErrorCode, getValidationFindings } from '@/lib/api-error'
import { cn } from '@/lib/utils'

const UPLOAD_TABS: Array<{ id: VersionUploadTab; label: string }> = [
  { id: 'file', label: 'Upload File' },
  { id: 'paste', label: 'Paste JSON' },
  { id: 'templates', label: 'Templates' },
]

interface VersionUploadDialogProps {
  gameId: string
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function VersionUploadDialog({
  gameId,
  open,
  onOpenChange,
}: VersionUploadDialogProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const createVersion = useCreateGameVersion(gameId)
  const templates = useGameTemplates()
  const [activeTab, setActiveTab] = useState<VersionUploadTab>('file')
  const [fileName, setFileName] = useState<string | null>(null)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>()

  const {
    register,
    handleSubmit,
    setValue,
    reset,
    watch,
    formState: { errors },
  } = useForm<VersionUploadFormValues>({
    resolver: zodResolver(versionUploadSchema),
    defaultValues: {
      engineVersion: DEFAULT_ENGINE_VERSION,
      canonicalJsonText: JSON.stringify({ schemaVersion: '1.0.0' }, null, 2),
    },
  })

  const canonicalJsonText = watch('canonicalJsonText')

  const validationFindings =
    createVersion.isError && getApiErrorCode(createVersion.error) === 'VALIDATION_FAILED'
      ? getValidationFindings(createVersion.error)
      : []

  const duplicateDetails = createVersion.isError
    ? getDuplicateVersionDetails(createVersion.error)
    : null

  function handleClose(nextOpen: boolean) {
    if (!nextOpen) {
      reset()
      createVersion.reset()
      setUploadError(null)
      setFileName(null)
      setSelectedTemplateId(undefined)
      setActiveTab('file')
    }
    onOpenChange(nextOpen)
  }

  function applyTemplate(template: GameTemplate) {
    setSelectedTemplateId(template.id)
    setValue('canonicalJsonText', JSON.stringify(template.canonicalJson, null, 2), {
      shouldValidate: true,
    })
    setUploadError(null)
    setFileName(null)
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-h-[90vh] max-w-2xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Upload game version</DialogTitle>
          <DialogDescription>
            Upload a canonical JSON file, paste JSON, or start from a template.
            Validation runs before the version is saved.
          </DialogDescription>
        </DialogHeader>

        <div className="flex gap-1 rounded-lg border p-1">
          {UPLOAD_TABS.map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'flex-1 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                activeTab === tab.id
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
              )}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <form
          className="space-y-4"
          onSubmit={handleSubmit((values) => {
            createVersion.mutate({
              canonicalJson: parseCanonicalJson(values.canonicalJsonText),
              engineVersion: values.engineVersion,
            })
          })}
        >
          {activeTab === 'file' && (
            <div className="space-y-3">
              <input
                ref={fileInputRef}
                type="file"
                accept="application/json,.json"
                className="hidden"
                onChange={async (event) => {
                  const file = event.target.files?.[0]
                  if (!file) return
                  setFileName(file.name)
                  try {
                    const text = await file.text()
                    JSON.parse(text)
                    setValue('canonicalJsonText', text, { shouldValidate: true })
                    setUploadError(null)
                  } catch {
                    setUploadError('Selected file does not contain valid JSON')
                  }
                }}
              />
              <Button
                type="button"
                variant="outline"
                onClick={() => fileInputRef.current?.click()}
              >
                <Upload className="h-4 w-4" />
                Choose JSON file
              </Button>
              {fileName && (
                <p className="flex items-center gap-2 text-sm text-muted-foreground">
                  <FileJson className="h-4 w-4" />
                  {fileName}
                </p>
              )}
            </div>
          )}

          {activeTab === 'paste' && (
            <div className="space-y-2">
              <Label htmlFor="canonical-json">Canonical JSON</Label>
              <Textarea
                id="canonical-json"
                rows={14}
                className="font-mono text-xs"
                {...register('canonicalJsonText')}
              />
            </div>
          )}

          {activeTab === 'templates' && (
            <div className="space-y-3">
              <p className="text-sm text-muted-foreground">
                Pick a template to load canonical JSON into this upload.
              </p>
              <TemplateSelector
                templates={templates}
                selectedId={selectedTemplateId}
                onSelect={applyTemplate}
              />
            </div>
          )}

          {uploadError && <p className="text-sm text-destructive">{uploadError}</p>}
          {errors.canonicalJsonText && (
            <p className="text-sm text-destructive">
              {errors.canonicalJsonText.message}
            </p>
          )}

          {activeTab !== 'paste' && canonicalJsonText && (
            <p className="text-xs text-muted-foreground">
              {canonicalJsonText.trim().length.toLocaleString()} characters loaded
            </p>
          )}

          <div className="space-y-2">
            <Label htmlFor="engine-version">Engine version</Label>
            <Input id="engine-version" {...register('engineVersion')} />
            {errors.engineVersion && (
              <p className="text-sm text-destructive">{errors.engineVersion.message}</p>
            )}
          </div>

          {validationFindings.length > 0 && (
            <div className="space-y-2 rounded-lg border border-destructive/30 bg-destructive/5 p-4">
              <p className="text-sm font-medium text-destructive">
                Validation failed ({validationFindings.length} findings)
              </p>
              <ValidationFindingsTable findings={validationFindings} />
            </div>
          )}

          {duplicateDetails && (
            <DuplicateVersionNotice
              details={duplicateDetails}
              onCancel={() => handleClose(false)}
            />
          )}

          {!duplicateDetails && (
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => handleClose(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={createVersion.isPending}>
                {createVersion.isPending ? 'Uploading…' : 'Create version'}
              </Button>
            </DialogFooter>
          )}
        </form>
      </DialogContent>
    </Dialog>
  )
}
