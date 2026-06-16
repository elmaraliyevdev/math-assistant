import { Link } from '@tanstack/react-router'
import { useState } from 'react'

import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import {
  TemplateDownloadCard,
  UseTemplateDialog,
  useGameTemplates,
} from '@/features/game-templates'
import type { GameTemplate } from '@/features/game-templates/types'

export function TemplatesPage() {
  const templates = useGameTemplates()
  const [selectedTemplate, setSelectedTemplate] = useState<GameTemplate | null>(null)

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Game Templates</h2>
        <p className="text-muted-foreground">
          Download canonical JSON templates or upload your own JSON from a game&apos;s
          detail page.
        </p>
      </div>

      <Card>
        <CardContent className="flex flex-col gap-3 pt-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="font-medium">Upload your own canonical JSON</p>
            <p className="text-sm text-muted-foreground">
              Open a game, then use Upload JSON to pick a file or paste JSON.
            </p>
          </div>
          <Button variant="outline" asChild>
            <Link to="/games">Go to games</Link>
          </Button>
        </CardContent>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        {templates.map((template) => (
          <TemplateDownloadCard
            key={template.id}
            template={template}
            onUseTemplate={setSelectedTemplate}
          />
        ))}
      </div>

      <UseTemplateDialog
        template={selectedTemplate}
        open={Boolean(selectedTemplate)}
        onOpenChange={(open) => {
          if (!open) setSelectedTemplate(null)
        }}
      />
    </div>
  )
}
