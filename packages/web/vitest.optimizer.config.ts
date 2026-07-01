import path from 'node:path'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json-summary'],
      include: ['src/features/reel-studio/optimizer/**/*.ts'],
      exclude: ['src/features/reel-studio/optimizer/context/**', 'src/features/reel-studio/optimizer/components/**'],
      thresholds: {
        lines: 90,
        statements: 89,
        functions: 89,
        branches: 62,
      },
    },
  },
})
