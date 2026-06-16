export interface GameTemplate {
  id: string
  name: string
  description: string
  features: string[]
  filename: string
  canonicalJson: Record<string, unknown>
}

export type VersionUploadTab = 'file' | 'paste' | 'templates'
