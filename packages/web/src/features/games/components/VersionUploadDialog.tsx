import { zodResolver } from '@hookform/resolvers/zod'
import { FileJson, Sparkles, Upload } from 'lucide-react'
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

const SOURCE_OPTIONS: Array<{ id: VersionUploadTab; label: string; description: string }> = [
  { id: 'file', label: 'Upload JSON', description: 'Choose a canonical JSON file' },
  { id: 'paste', label: 'Paste JSON', description: 'Paste canonical JSON directly' },
  { id: 'templates', label: 'Use template', description: 'Start from a game template' },
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
  const createVersion = useCreateGameVersion(gameId, { navigateTo: 'studio' })
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
          <DialogTitle>Create version</DialogTitle>
          <DialogDescription>
            Choose a source for your new mathematical design. You&apos;ll continue in the
            Design Studio after creation.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-2">
          <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
            Choose source
          </p>
          <div className="grid gap-2 sm:grid-cols-3">
            {SOURCE_OPTIONS.map((option) => (
              <button
                key={option.id}
                type="button"
                onClick={() => setActiveTab(option.id)}
                className={cn(
                  'rounded-xl border p-3 text-left transition-all duration-200',
                  activeTab === option.id
                    ? 'border-primary/50 bg-primary/5 ring-1 ring-primary/30'
                    : 'border-border/60 hover:bg-muted/30',
                )}
              >
                <p className="text-sm font-medium">{option.label}</p>
                <p className="mt-1 text-xs text-muted-foreground">{option.description}</p>
              </button>
            ))}
          </div>
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
            <div className="space-y-3 rounded-xl bg-muted/20 p-4 ring-1 ring-border/30">
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
                Pick a template to start your new version.
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
            <p className="text-sm text-destructive">{errors.canonicalJsonText.message}</p>
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
              <Button
                type="submit"
                disabled={createVersion.isPending}
              >
                <Sparkles className="h-4 w-4" />
                {createVersion.isPending ? 'Creating…' : 'Create version'}
              </Button>
            </DialogFooter>
          )}
        </form>
      </DialogContent>
    </Dialog>
  )
}
