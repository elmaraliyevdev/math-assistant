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
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (requestPath) => requestPath.replace(/^\/api/, ''),
      },
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json-summary'],
      include: [
        'src/components/mobile-nav.tsx',
        'src/components/empty-state.tsx',
        'src/components/glossary-term.tsx',
        'src/lib/glossary.ts',
        'src/lib/navigation.ts',
        'src/features/onboarding/progress.ts',
        'src/features/onboarding/components/OnboardingProgressHeader.tsx',
      ],
      exclude: [
        'src/main.tsx',
        'src/vite-env.d.ts',
        'src/features/game-templates/index.ts',
      ],
      thresholds: {
        lines: 90,
        statements: 90,
        functions: 90,
        branches: 85,
      },
    },
  },
})
