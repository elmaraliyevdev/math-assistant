/**
 * @deprecated Use `node packages/brand/scripts/sync-assets.mjs` directly.
 * Kept so existing `npm run sync:brand` in packages/web continues to work.
 */
import { spawnSync } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const syncScript = path.resolve(__dirname, '../../brand/scripts/sync-assets.mjs')

const result = spawnSync(process.execPath, [syncScript], { stdio: 'inherit' })
process.exit(result.status ?? 1)
