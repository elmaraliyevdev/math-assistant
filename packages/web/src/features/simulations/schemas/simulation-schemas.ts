import { z } from 'zod'

export const simulationFormSchema = z.object({
  gameId: z.string().min(1, 'Select a game'),
  gameVersionId: z.string().uuid('Select a game version'),
  spinCount: z.number().int().min(1, 'Spin count must be at least 1'),
  betMinorUnits: z.number().int().min(0, 'Bet must be zero or greater'),
  masterSeed: z.string().optional(),
  eventLogMode: z.enum(['none', 'summary', 'full']),
})

export type SimulationFormValues = z.infer<typeof simulationFormSchema>
