export type TemplateCategory =
  | 'popular'
  | 'classic'
  | 'hold-win'
  | 'megaways'
  | 'free-spins'
  | 'jackpot'
  | 'experimental'
  | 'recent'

export type TemplateDifficulty = 'beginner' | 'intermediate' | 'advanced'

export interface GameTemplate {
  id: string
  name: string
  description: string
  features: string[]
  filename: string
  canonicalJson: Record<string, unknown>
  categories: TemplateCategory[]
  rtp?: number
  difficulty?: TemplateDifficulty
  provider?: string
  certified?: boolean
  featureChips?: string[]
}

export type VersionUploadTab = 'file' | 'paste' | 'templates'
