import { copyFileSync, existsSync, mkdirSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const brandRoot = path.resolve(__dirname, '..')
const repoRoot = path.resolve(brandRoot, '../..')
const assetsDir = path.join(brandRoot, 'assets')

const files = [
  ['logo.svg', 'logo.svg'],
  ['logo-white.svg', 'logo-white.svg'],
  ['black-logo-icon.svg', 'black-logo-icon.svg'],
  ['white-logo-icon.svg', 'white-logo-icon.svg'],
  ['white-logo-icon.svg', 'favicon.svg'],
  ['black-logo-icon.svg', 'logo-icon.svg'],
  ['white-logo-icon.svg', 'logo-icon-white.svg'],
]

const consumerTargets = [
  path.join(repoRoot, 'packages/web/public'),
  path.join(repoRoot, 'packages/web/src/assets/brand'),
  path.join(repoRoot, 'math-studio-lp/public'),
]

function resolveSource(sourceName) {
  const candidates = [
    path.join(assetsDir, sourceName),
    path.join(repoRoot, sourceName),
    path.join(repoRoot, 'packages/web/public', sourceName),
    path.join(repoRoot, 'packages/web/src/assets/brand', sourceName),
  ]
  return candidates.find((candidate) => existsSync(candidate))
}

for (const dir of consumerTargets) {
  mkdirSync(dir, { recursive: true })
}

let synced = 0
for (const [sourceName, destName] of files) {
  const source = resolveSource(sourceName)
  if (!source) {
    console.warn(`[brand/sync] missing ${sourceName}`)
    continue
  }
  for (const dir of consumerTargets) {
    copyFileSync(source, path.join(dir, destName))
  }
  synced += 1
}

console.log(`[brand/sync] synced ${synced} asset(s) to ${consumerTargets.length} target(s)`)
