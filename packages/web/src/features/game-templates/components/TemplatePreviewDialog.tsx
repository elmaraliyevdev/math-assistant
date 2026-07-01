import { Download, Sparkles } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { downloadTemplate } from '@/features/game-templates/api/templates-api'
import { TemplatePreview } from '@/features/game-templates/components/TemplatePreview'
import type { GameTemplate } from '@/features/game-templates/types'
import { formatPercent } from '@/lib/utils'

interface TemplatePreviewDialogProps {
  template: GameTemplate
  open: boolean
  onOpenChange: (open: boolean) => void
  onUseTemplate: (template: GameTemplate) => void
}

function readMeta(template: GameTemplate, key: string): string | number | undefined {
  const meta = template.canonicalJson.metadata as Record<string, unknown> | undefined
  const value = meta?.[key]
  if (typeof value === 'string' || typeof value === 'number') return value
  const game = template.canonicalJson.game as Record<string, unknown> | undefined
  const gameValue = game?.[key]
  if (typeof gameValue === 'string' || typeof gameValue === 'number') return gameValue
  return undefined
}

export function TemplatePreviewDialog({
  template,
  open,
  onOpenChange,
  onUseTemplate,
}: TemplatePreviewDialogProps) {
  const reels = readMeta(template, 'reels') ?? readMeta(template, 'reelCount') ?? '5×3'
  const paylines = readMeta(template, 'paylines') ?? '10'

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] max-w-3xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{template.name}</DialogTitle>
        </DialogHeader>

        <Tabs defaultValue="overview">
          <TabsList className="mb-3">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="paylines">Paylines</TabsTrigger>
            <TabsTrigger value="features">Features</TabsTrigger>
            <TabsTrigger value="symbols">Symbols</TabsTrigger>
            <TabsTrigger value="rtp">RTP</TabsTrigger>
            <TabsTrigger value="json">JSON</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-3 text-sm">
            <p className="text-muted-foreground">{template.description}</p>
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline">Reels {String(reels)}</Badge>
              <Badge variant="outline">Paylines {String(paylines)}</Badge>
              {template.rtp ? (
                <Badge variant="outline">{formatPercent(template.rtp, 1)} RTP</Badge>
              ) : null}
            </div>
          </TabsContent>

          <TabsContent value="paylines" className="text-sm text-muted-foreground">
            Canonical template defines {String(paylines)} paylines. Open JSON for full geometry.
          </TabsContent>

          <TabsContent value="features" className="space-y-2 text-sm">
            {template.features.map((feature) => (
              <p key={feature}>• {feature}</p>
            ))}
          </TabsContent>

          <TabsContent value="symbols" className="text-sm text-muted-foreground">
            Symbol set is defined in the canonical JSON symbols array.
          </TabsContent>

          <TabsContent value="rtp" className="text-sm">
            {template.rtp ? (
              <p>Theoretical RTP target: {formatPercent(template.rtp, 2)}</p>
            ) : (
              <p className="text-muted-foreground">RTP not specified in template metadata.</p>
            )}
          </TabsContent>

          <TabsContent value="json">
            <TemplatePreview template={template} />
          </TabsContent>
        </Tabs>

        <DialogFooter>
          <Button variant="outline" onClick={() => downloadTemplate(template)}>
            <Download className="h-4 w-4" />
            Download
          </Button>
          <Button
            onClick={() => {
              onUseTemplate(template)
              onOpenChange(false)
            }}
          >
            <Sparkles className="h-4 w-4" />
            Use template
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
