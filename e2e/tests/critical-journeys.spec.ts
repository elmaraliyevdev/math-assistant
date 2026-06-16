import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

import { expect, test } from '@playwright/test'

const __dirname = dirname(fileURLToPath(import.meta.url))
const canonicalJson = readFileSync(
  join(__dirname, '../fixtures/game.canonical.json'),
  'utf-8',
)

function uniqueEmail(prefix: string) {
  return `${prefix}-${Date.now()}@e2e.example.com`
}

test.describe('critical user journeys', () => {
  test('registration and login', async ({ page }) => {
    const email = uniqueEmail('register')
    const password = 'E2E-secure-password-1'

    await page.goto('/register')
    await page.getByLabel('Full name').fill('E2E Tester')
    await page.getByLabel('Email').fill(email)
    await page.getByLabel('Password').fill(password)
    await page.getByRole('button', { name: /create account/i }).click()

    await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible()

    await page.getByRole('button', { name: /sign out/i }).click()
    await expect(page).toHaveURL(/\/login/)

    await page.getByLabel('Email').fill(email)
    await page.getByLabel('Password').fill(password)
    await page.getByRole('button', { name: /sign in/i }).click()
    await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible()
  })

  test('organization, game, version, simulation, analytics, notifications, settings', async ({
    page,
  }) => {
    const email = uniqueEmail('journey')
    const password = 'E2E-secure-password-1'
    const gameName = `E2E Game ${Date.now()}`

    await page.goto('/register')
    await page.getByLabel('Full name').fill('Journey Tester')
    await page.getByLabel('Email').fill(email)
    await page.getByLabel('Password').fill(password)
    await page.getByRole('button', { name: /create account/i }).click()
    await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible()

    await page.goto('/organizations/settings')
    await page.locator('#new-org-name').fill('Beta Studio')
    await page.locator('#new-org-slug').fill(`beta-studio-${Date.now()}`)
    await page.getByRole('button', { name: /create organization/i }).click()
    await expect(page.getByText(/beta studio/i)).toBeVisible()

    await page.goto('/games/create')
    await page.locator('#game-name').fill(gameName)
    await page.getByRole('button', { name: /create game/i }).click()
    await expect(page.getByRole('heading', { name: gameName })).toBeVisible()

    await page.getByRole('button', { name: /upload new version/i }).click()
    await page.locator('#canonical-json').fill(canonicalJson)
    await page.getByRole('button', { name: /create version/i }).click()
    await expect(page.getByText(/v1/i)).toBeVisible({ timeout: 30_000 })

    await page.goto('/simulations/create')
    await page.getByLabel('Game').click()
    await page.getByRole('option', { name: gameName }).click()
    await page.getByLabel('Spin count').fill('50')
    await page.getByRole('button', { name: /start simulation/i }).click()
    await expect(page.getByRole('heading', { name: /simulation/i })).toBeVisible()

    await expect(page.getByText(/completed/i)).toBeVisible({ timeout: 90_000 })
    await expect(page.getByText(/rtp/i).first()).toBeVisible()

    await page.getByRole('button', { name: /notifications/i }).click()
    await expect(page.getByText(/simulation completed/i)).toBeVisible()

    await page.goto('/settings')
    await expect(page.getByRole('heading', { name: /settings/i })).toBeVisible()
    await page.getByLabel('Full name').fill('Journey Updated')
    await page.getByRole('button', { name: /save profile/i }).click()

    await page.goto('/audit')
    await expect(page.getByText(/auth\.login|game\.create|simulation\.create/)).toBeVisible()
  })
})
