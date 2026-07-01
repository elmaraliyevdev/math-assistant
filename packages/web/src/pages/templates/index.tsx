import { Link } from '@tanstack/react-router'
import { Search } from 'lucide-react'
import { useMemo, useState } from 'react'

import { PageHeader, PageLayout } from '@/components/design-system'
import { EmptyState } from '@/components/design-system'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  GAME_TEMPLATES,
  TEMPLATE_CATEGORY_TABS,
} from '@/features/game-templates/api/templates-api'
import { TemplateCard } from '@/features/game-templates/components/TemplateCard'
import { UseTemplateDialog } from '@/features/game-templates/components/UseTemplateDialog'
import {
  getFavoriteTemplateIds,
  getRecentTemplateIds,
  markTemplateUsed,
  toggleFavoriteTemplate,
} from '@/features/game-templates/lib/template-preferences'
import type { GameTemplate } from '@/features/game-templates/types'
import { AiHelpLink } from '@/features/settings/components/settings-primitives'

export function TemplatesPage() {
  const [category, setCategory] = useState<string>('popular')
  const [search, setSearch] = useState('')
  const [provider, setProvider] = useState('all')
  const [difficulty, setDifficulty] = useState('all')
  const [certification, setCertification] = useState('all')
  const [rtpMin, setRtpMin] = useState('all')
  const [selectedTemplate, setSelectedTemplate] = useState<GameTemplate | null>(null)
  const [favorites, setFavorites] = useState(getFavoriteTemplateIds)
  const [recentIds] = useState(getRecentTemplateIds)

  const templates = useMemo(() => {
    return GAME_TEMPLATES.filter((template) => {
      if (category === 'favorites' && !favorites.includes(template.id)) return false
      if (category === 'recent' && !recentIds.includes(template.id)) return false
      if (
        category !== 'favorites' &&
        category !== 'recent' &&
        !template.categories.includes(category as GameTemplate['categories'][number])
      ) {
        return false
      }
      if (provider !== 'all' && template.provider !== provider) return false
      if (difficulty !== 'all' && template.difficulty !== difficulty) return false
      if (certification === 'certified' && !template.certified) return false
      if (certification === 'uncertified' && template.certified) return false
      if (rtpMin === '95' && (template.rtp ?? 0) < 0.95) return false
      if (rtpMin === '96' && (template.rtp ?? 0) < 0.96) return false
      if (!search.trim()) return true
      const haystack = [template.name, template.description, ...template.features]
        .join(' ')
        .toLowerCase()
      return haystack.includes(search.toLowerCase())
    })
  }, [category, certification, difficulty, favorites, provider, recentIds, rtpMin, search])

  const handleUseTemplate = (template: GameTemplate) => {
    markTemplateUsed(template.id)
    setSelectedTemplate(template)
  }

  return (
    <PageLayout className="space-y-4">
      <PageHeader
        title="Templates"
        description="Discover official game templates or upload canonical JSON from a game."
        className="mb-4"
        actions={
          <div className="flex gap-2">
            <AiHelpLink prompt="Which template fits a Hold & Win game with 96% RTP?" />
            <Button variant="outline" size="sm" asChild>
              <Link to="/games">Go to games</Link>
            </Button>
          </div>
        }
      />

      <Tabs value={category} onValueChange={setCategory}>
        <TabsList className="h-auto flex-wrap justify-start">
          {TEMPLATE_CATEGORY_TABS.map((tab) => (
            <TabsTrigger key={tab.id} value={tab.id} className="text-xs sm:text-sm">
              {tab.label}
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>

      <div className="flex flex-col gap-2 rounded-lg border border-border/60 p-2 lg:flex-row lg:items-center">
        <div className="relative min-w-[180px] flex-1">
          <Search className="pointer-events-none absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            className="pl-8"
            placeholder="Search templates…"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>
        <Select value={provider} onValueChange={setProvider}>
          <SelectTrigger className="w-full lg:w-36">
            <SelectValue placeholder="Provider" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All providers</SelectItem>
            <SelectItem value="Official">Official</SelectItem>
          </SelectContent>
        </Select>
        <Select value={rtpMin} onValueChange={setRtpMin}>
          <SelectTrigger className="w-full lg:w-28">
            <SelectValue placeholder="RTP" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Any RTP</SelectItem>
            <SelectItem value="95">95%+</SelectItem>
            <SelectItem value="96">96%+</SelectItem>
          </SelectContent>
        </Select>
        <Select value={difficulty} onValueChange={setDifficulty}>
          <SelectTrigger className="w-full lg:w-36">
            <SelectValue placeholder="Difficulty" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Any difficulty</SelectItem>
            <SelectItem value="beginner">Beginner</SelectItem>
            <SelectItem value="intermediate">Intermediate</SelectItem>
            <SelectItem value="advanced">Advanced</SelectItem>
          </SelectContent>
        </Select>
        <Select value={certification} onValueChange={setCertification}>
          <SelectTrigger className="w-full lg:w-36">
            <SelectValue placeholder="Certification" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All</SelectItem>
            <SelectItem value="certified">Certified</SelectItem>
            <SelectItem value="uncertified">Uncertified</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {templates.length === 0 ? (
        <EmptyState
          title="No templates yet"
          description="Try another category or create your first game from an official template."
          action={
            <Button size="sm" onClick={() => setCategory('popular')}>
              Browse popular templates
            </Button>
          }
        />
      ) : (
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {templates.map((template) => (
            <TemplateCard
              key={template.id}
              template={template}
              favorite={favorites.includes(template.id)}
              onToggleFavorite={(id) => setFavorites(toggleFavoriteTemplate(id))}
              onUseTemplate={handleUseTemplate}
            />
          ))}
        </div>
      )}

      <UseTemplateDialog
        template={selectedTemplate}
        open={Boolean(selectedTemplate)}
        onOpenChange={(open) => {
          if (!open) setSelectedTemplate(null)
        }}
      />
    </PageLayout>
  )
}
