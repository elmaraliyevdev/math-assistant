export const SUGGESTED_PROMPTS = [
  'Analyze my RTP',
  'Explain why certification failed',
  'Recommend reel improvements',
  'Compare two simulations',
  'How can I increase volatility?',
  'Optimize hit frequency',
  'Explain feature contribution',
  'Improve scatter distribution',
  'Why is my design health only 72?',
  'Generate certification checklist',
] as const

export const QUICK_ACTIONS = [
  'Analyze RTP',
  'Recommend improvements',
  'Review constraints',
  'Explain volatility',
  'Generate report',
] as const

export const SLASH_COMMANDS: Array<{ command: string; prompt: string }> = [
  { command: '/analyze', prompt: 'Analyze RTP decomposition and feature contribution.' },
  { command: '/compare', prompt: 'Compare these simulations and explain RTP differences.' },
  { command: '/explain', prompt: 'Explain the mathematical design and risk profile.' },
  { command: '/optimize', prompt: 'Recommend tuning actions to improve RTP toward target.' },
  { command: '/review', prompt: 'Review certification readiness and highlight blockers.' },
  { command: '/generate', prompt: 'Generate a certification checklist for this version.' },
]

export function resolveSlashCommand(input: string): string | null {
  const trimmed = input.trim().toLowerCase()
  const match = SLASH_COMMANDS.find((item) => trimmed.startsWith(item.command))
  if (!match) return null
  const rest = input.trim().slice(match.command.length).trim()
  return rest ? `${match.prompt} ${rest}` : match.prompt
}

export function followUpsForMode(mode: 'simulation' | 'compare' | 'game-version') {
  if (mode === 'compare') {
    return [
      'Explain the largest RTP delta',
      'Which run is certification-ready?',
      'Recommend which version to ship',
    ]
  }
  if (mode === 'game-version') {
    return [
      'Open in Studio',
      'Run a validation simulation',
      'Explain scatter triggers',
      'Review paytable balance',
    ]
  }
  return [
    'Compare with previous version',
    'Generate tuning plan',
    'Explain recommendation impact',
    'Run optimization',
    'Open Studio',
  ]
}
