import simpleTemplate from '../../../web/src/features/game-templates/templates/simple-5x3.json'
import { parseCanonicalJson } from '@/features/reel-studio/lib/parse-canonical'

import { DEMO_ENGINE_VERSION } from './constants'

export const demoReelStudioDocument = parseCanonicalJson(
  simpleTemplate as Record<string, unknown>,
  DEMO_ENGINE_VERSION,
)
