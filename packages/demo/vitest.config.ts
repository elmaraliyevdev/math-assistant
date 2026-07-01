import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { defineConfig } from 'vitest/config'

const root = path.dirname(fileURLToPath(import.meta.url))
const webSrc = path.resolve(root, '../web/src')

export default defineConfig({
  resolve: {
    alias: {
      '@': webSrc,
      '@web/types': path.join(webSrc, 'types'),
      '@web/types/api': path.join(webSrc, 'types/api.ts'),
      '@/lib/utils': path.join(webSrc, 'lib/utils.ts'),
    },
  },
  test: {
    environment: 'jsdom',
    include: ['tests/**/*.test.ts', 'tests/**/*.test.tsx'],
  },
})
