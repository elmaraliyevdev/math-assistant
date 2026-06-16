export const GLOSSARY = {
  rtp: {
    label: 'RTP',
    definition:
      'Return to Player — the long-run percentage of wagered stakes returned as wins. Expressed as a decimal or percentage.',
  },
  hitFrequency: {
    label: 'Hit Frequency',
    definition:
      'The proportion of spins that produce any win. Higher hit frequency means more frequent but often smaller wins.',
  },
  volatility: {
    label: 'Volatility',
    definition:
      'A measure of payout swinginess. Higher volatility means larger but less frequent wins relative to the bet.',
  },
  confidenceInterval: {
    label: 'Confidence Interval',
    definition:
      'A statistical range around the simulated RTP that estimates where the true value likely falls at a given confidence level.',
  },
  exposureCap: {
    label: 'Exposure Cap',
    definition:
      'The maximum win allowed per spin or session. Wins above the cap are truncated, affecting capped vs uncapped RTP.',
  },
  minorUnits: {
    label: 'Minor Units',
    definition:
      'Integer bet amounts in the smallest currency unit (e.g. cents). Avoids floating-point rounding in calculations.',
  },
  determinism: {
    label: 'Determinism',
    definition:
      'When a master seed is set, the same configuration reproduces identical outcomes for auditability and regression testing.',
  },
} as const

export type GlossaryTermKey = keyof typeof GLOSSARY

export function getGlossaryDefinition(term: GlossaryTermKey): string {
  return GLOSSARY[term].definition
}
