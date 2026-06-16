import { Download, Eye, Sparkles } from 'lucide-react'
import { useState } from 'react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { TemplatePreview } from '@/features/game-templates/components/TemplatePreview'
import { downloadTemplate } from '@/features/game-templates/api/templates-api'
import type { GameTemplate } from '@/features/game-templates/types'

interface TemplateDownloadCardProps {
  template: GameTemplate
  onUseTemplate: (template: GameTemplate) => void
}

export function TemplateDownloadCard({
  template,
  onUseTemplate,
}: TemplateDownloadCardProps) {
  const [previewOpen, setPreviewOpen] = useState(false)

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">{template.name}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">{template.description}</p>
          <ul className="list-inside list-disc text-sm text-muted-foreground">
            {template.features.map((feature) => (
              <li key={feature}>{feature}</li>
            ))}
          </ul>
          <div className="flex flex-wrap gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => downloadTemplate(template)}
            >
              <Download className="h-4 w-4" />
              Download JSON
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPreviewOpen(true)}
            >
              <Eye className="h-4 w-4" />
              Preview
            </Button>
            <Button size="sm" onClick={() => onUseTemplate(template)}>
              <Sparkles className="h-4 w-4" />
              Use Template
            </Button>
          </div>
        </CardContent>
      </Card>

      <Dialog open={previewOpen} onOpenChange={setPreviewOpen}>
        <DialogContent className="max-h-[90vh] max-w-3xl overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{template.name}</DialogTitle>
          </DialogHeader>
          <TemplatePreview template={template} />
        </DialogContent>
      </Dialog>
    </>
  )
}
