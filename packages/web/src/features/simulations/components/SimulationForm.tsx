import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useGameVersions } from '@/features/games/hooks/use-games'
import { SimulationLimitsNotice } from '@/features/simulations/components/SimulationLimitsNotice'
import { useSimulationLimits } from '@/features/simulations/hooks/use-simulation-limits'
import {
  simulationFormSchema,
  type SimulationFormValues,
} from '@/features/simulations/schemas/simulation-schemas'
import { GlossaryTerm } from '@/components/glossary-term'
import { FieldLabel } from '@/features/workbench/components/FieldHelp'
import { RuntimeEstimateNotice } from '@/features/workbench/components/RuntimeEstimateNotice'
import { SpinCountPresets } from '@/features/workbench/components/SpinCountPresets'
import { useSimulationThroughput } from '@/features/workbench/hooks/use-workbench'
import type { Game } from '@/types/api'

interface SimulationFormProps {
  games: Game[]
  defaultValues?: Partial<SimulationFormValues>
  submitLabel?: string
  loading?: boolean
  onSubmit: (values: SimulationFormValues) => void
  onCancel?: () => void
}

export function SimulationForm({
  games,
  defaultValues,
  submitLabel = 'Start simulation',
  loading = false,
  onSubmit,
  onCancel,
}: SimulationFormProps) {
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<SimulationFormValues>({
    resolver: zodResolver(simulationFormSchema),
    defaultValues: {
      gameId: '',
      gameVersionId: '',
      spinCount: 1000,
      betMinorUnits: 100,
      masterSeed: '',
      eventLogMode: 'none',
      ...defaultValues,
    },
  })

  const gameId = watch('gameId')
  const spinCount = watch('spinCount')
  const versions = useGameVersions(gameId)
  const limits = useSimulationLimits(spinCount)
  const throughput = useSimulationThroughput()
  const submitBlocked =
    limits.spinCountExceeded || limits.activeLimitReached || limits.isLoading

  useEffect(() => {
    if (!gameId) {
      setValue('gameVersionId', '')
      return
    }

    const firstVersion = versions.data?.[0]
    if (firstVersion && !defaultValues?.gameVersionId) {
      setValue('gameVersionId', firstVersion.id)
    }
  }, [defaultValues?.gameVersionId, gameId, setValue, versions.data])

  return (
    <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
      <SimulationLimitsNotice spinCount={spinCount} />
      <div className="space-y-2">
        <Label htmlFor="sim-game">Game</Label>
        <Select
          value={gameId}
          onValueChange={(value) => {
            setValue('gameId', value, { shouldValidate: true })
            setValue('gameVersionId', '')
          }}
        >
          <SelectTrigger id="sim-game">
            <SelectValue placeholder="Select a game" />
          </SelectTrigger>
          <SelectContent>
            {games.map((game) => (
              <SelectItem key={game.id} value={game.id}>
                {game.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {errors.gameId && (
          <p className="text-sm text-destructive">{errors.gameId.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="sim-version">Game version</Label>
        <Select
          value={watch('gameVersionId')}
          onValueChange={(value) =>
            setValue('gameVersionId', value, { shouldValidate: true })
          }
          disabled={!gameId || versions.isLoading}
        >
          <SelectTrigger id="sim-version">
            <SelectValue placeholder="Select a version" />
          </SelectTrigger>
          <SelectContent>
            {(versions.data ?? []).map((version) => (
              <SelectItem key={version.id} value={version.id}>
                v{version.version}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {errors.gameVersionId && (
          <p className="text-sm text-destructive">
            {errors.gameVersionId.message}
          </p>
        )}
      </div>

      <div className="space-y-2">
        <FieldLabel
          htmlFor="sim-spin-count"
          label="Spin count"
          description="Higher spin counts improve statistical confidence. Use 100K+ for calibration and 1M+ for certification-grade confidence."
        />
        <SpinCountPresets
          value={spinCount}
          maxSpinCount={limits.limits?.maxSimulationSpinCount}
          onSelect={(value) => setValue('spinCount', value, { shouldValidate: true })}
        />
        <Input
          id="sim-spin-count"
          type="number"
          {...register('spinCount', { valueAsNumber: true })}
        />
        <RuntimeEstimateNotice
          spinCount={spinCount}
          spinsPerSecond={throughput.data?.spinsPerSecond}
          source={throughput.data?.source}
          sampleCount={throughput.data?.sampleCount}
        />
        {errors.spinCount && (
          <p className="text-sm text-destructive">{errors.spinCount.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <div className="flex items-center gap-1">
          <Label htmlFor="sim-bet">
            <GlossaryTerm term="minorUnits">Bet (minor units)</GlossaryTerm>
          </Label>
        </div>
        <Input
          id="sim-bet"
          type="number"
          {...register('betMinorUnits', { valueAsNumber: true })}
        />
        {errors.betMinorUnits && (
          <p className="text-sm text-destructive">
            {errors.betMinorUnits.message}
          </p>
        )}
      </div>

      <div className="space-y-2">
        <div className="flex items-center gap-1">
          <Label htmlFor="sim-seed">
            <GlossaryTerm term="determinism">Master seed (optional)</GlossaryTerm>
          </Label>
        </div>
        <Input id="sim-seed" {...register('masterSeed')} />
      </div>

      <div className="space-y-2">
        <FieldLabel
          htmlFor="sim-event-log"
          label="Event log mode"
          description="None is fastest. Summary captures aggregate events. Full logs every event and increases runtime and storage."
        />
        <Select
          value={watch('eventLogMode')}
          onValueChange={(value: SimulationFormValues['eventLogMode']) =>
            setValue('eventLogMode', value, { shouldValidate: true })
          }
        >
          <SelectTrigger id="sim-event-log">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none">None</SelectItem>
            <SelectItem value="summary">Summary</SelectItem>
            <SelectItem value="full">Full</SelectItem>
          </SelectContent>
        </Select>
        {errors.eventLogMode && (
          <p className="text-sm text-destructive">
            {errors.eventLogMode.message}
          </p>
        )}
      </div>

      <div className="flex gap-2">
        <Button type="submit" disabled={loading || submitBlocked}>
          {loading ? 'Starting…' : submitLabel}
        </Button>
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
        )}
      </div>
    </form>
  )
}
