import { describe, expect, it } from 'vitest'
import { z } from 'zod'

const registerSchema = z.object({
  fullName: z.string().min(1),
  email: z.email(),
  password: z.string().min(8),
})

describe('register schema', () => {
  it('rejects short passwords', () => {
    const result = registerSchema.safeParse({
      fullName: 'Alice',
      email: 'alice@example.com',
      password: 'short',
    })
    expect(result.success).toBe(false)
  })

  it('accepts valid input', () => {
    const result = registerSchema.safeParse({
      fullName: 'Alice',
      email: 'alice@example.com',
      password: 'password123',
    })
    expect(result.success).toBe(true)
  })
})
