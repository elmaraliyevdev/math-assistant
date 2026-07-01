import { Download, Eye, Sparkles, Star } from 'lucide-react'
import { useState } from 'react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { downloadTemplate } from '@/features/game-templates/api/templates-api'
import { TemplatePreviewDialog } from '@/features/game-templates/components/TemplatePreviewDialog'
import type { GameTemplate } from '@/features/game-templates/types'
import { cn, formatPercent } from '@/lib/utils'

interface TemplateCardProps {
  template: GameTemplate
  favorite?: boolean
  onToggleFavorite?: (templateId: string) => void
  onUseTemplate: (template: GameTemplate) => void
}

export function TemplateCard({
  template,
  favorite,
  onToggleFavorite,
  onUseTemplate,
}: TemplateCardProps) {
  const [previewOpen, setPreviewOpen] = useState(false)

  return (
    <>
      <Card className="overflow-hidden transition-shadow hover:shadow-md">
        <CardContent className="space-y-3 p-4">
          <div className="flex items-start justify-between gap-2">
            <div>
              <h3 className="font-semibold">{template.name}</h3>
              {template.provider ? (
                <p className="text-xs text-muted-foreground">{template.provider}</p>
              ) : null}
            </div>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 shrink-0"
              onClick={() => onToggleFavorite?.(template.id)}
              aria-label={favorite ? 'Remove favorite' : 'Add favorite'}
            >
              <Star
                className={cn('h-4 w-4', favorite ? 'fill-amber-400 text-amber-400' : '')}
              />
            </Button>
          </div>

          <div className="flex flex-wrap gap-1.5">
            {(template.featureChips ?? template.features.slice(0, 3)).map((chip) => (
              <Badge key={chip} variant="secondary" className="font-normal">
                {chip}
              </Badge>
            ))}
            {template.rtp ? (
              <Badge variant="outline" className="font-normal">
                {formatPercent(template.rtp, 1)} RTP
              </Badge>
            ) : null}
            {template.difficulty ? (
              <Badge variant="outline" className="font-normal capitalize">
                {template.difficulty}
              </Badge>
            ) : null}
            {template.certified ? (
              <Badge className="font-normal">Certified</Badge>
            ) : null}
          </div>

          <p className="line-clamp-2 text-sm text-muted-foreground">{template.description}</p>

          <div className="flex flex-wrap gap-2 pt-1">
            <Button variant="outline" size="sm" onClick={() => setPreviewOpen(true)}>
              <Eye className="h-4 w-4" />
              Preview
            </Button>
            <Button variant="outline" size="sm" onClick={() => downloadTemplate(template)}>
              <Download className="h-4 w-4" />
              Download
            </Button>
            <Button size="sm" onClick={() => onUseTemplate(template)}>
              <Sparkles className="h-4 w-4" />
              Use
            </Button>
          </div>
        </CardContent>
      </Card>

      <TemplatePreviewDialog
        template={template}
        open={previewOpen}
        onOpenChange={setPreviewOpen}
        onUseTemplate={onUseTemplate}
      />
    </>
  )
}
