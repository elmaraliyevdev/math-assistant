import { Link, useNavigate } from '@tanstack/react-router'
import { ChevronLeft, ChevronRight, Sparkles } from 'lucide-react'
import { useState } from 'react'

import { VisualMeter } from '@/components/studio/VisualMeter'
import { PageHeader, PageLayout } from '@/components/design-system'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useCreateGame } from '@/features/games/hooks/use-games'
import { useCurrentOrganization } from '@/hooks/use-sync-organization'
import { useOrganizationStore } from '@/stores/organization-store'
import { cn } from '@/lib/utils'

type GridType = '5x3' | '6x4' | 'megaways' | 'cluster'
type Feature = 'wild' | 'scatter' | 'free_spins' | 'hold_win' | 'jackpot'
type Volatility = 'low' | 'medium' | 'high'

const GRID_OPTIONS: Array<{ id: GridType; label: string; detail: string }> = [
  { id: '5x3', label: '5×3', detail: 'Classic video slot' },
  { id: '6x4', label: '6×4', detail: 'Expanded grid' },
  { id: 'megaways', label: 'Megaways', detail: 'Variable reel heights' },
  { id: 'cluster', label: 'Cluster', detail: 'Cluster pays mechanic' },
]

const FEATURE_OPTIONS: Array<{ id: Feature; label: string }> = [
  { id: 'wild', label: 'Wild' },
  { id: 'scatter', label: 'Scatter' },
  { id: 'free_spins', label: 'Free Spins' },
  { id: 'hold_win', label: 'Hold & Win' },
  { id: 'jackpot', label: 'Jackpot' },
]

const STEPS = ['Basics', 'Features', 'Goals', 'Create'] as const

export function GameCreateWizard() {
  const navigate = useNavigate()
  const createGame = useCreateGame({ suppressNavigation: true })
  const currentOrg = useCurrentOrganization()
  const organizationId = useOrganizationStore((state) => state.currentOrganizationId)

  const [step, setStep] = useState(0)
  const [name, setName] = useState('')
  const [grid, setGrid] = useState<GridType>('5x3')
  const [features, setFeatures] = useState<Feature[]>(['wild', 'scatter'])
  const [targetRtp, setTargetRtp] = useState(96)
  const [volatility, setVolatility] = useState<Volatility>('medium')
  const [hitRate, setHitRate] = useState(28)
  const [maxWin, setMaxWin] = useState(5000)

  const toggleFeature = (feature: Feature) => {
    setFeatures((current) =>
      current.includes(feature)
        ? current.filter((item) => item !== feature)
        : [...current, feature],
    )
  }

  const buildDescription = () => {
    const featureLabels = features
      .map((id) => FEATURE_OPTIONS.find((item) => item.id === id)?.label ?? id)
      .join(', ')
    return [
      `Grid: ${grid}`,
      `Features: ${featureLabels || 'none'}`,
      `Target RTP: ${targetRtp}%`,
      `Volatility: ${volatility}`,
      `Hit rate: ${hitRate}%`,
      `Max win: ${maxWin}x`,
    ].join(' · ')
  }

  const handleCreate = () => {
    if (!organizationId || !name.trim()) return
    createGame.mutate(
      {
        organizationId,
        name: name.trim(),
        description: buildDescription(),
      },
      {
        onSuccess: (game) => {
          void navigate({ to: '/games/$gameId', params: { gameId: game.id } })
        },
      },
    )
  }

  return (
    <PageLayout className="max-w-2xl space-y-8">
      <PageHeader
        title="Create game"
        description={`Designing in ${currentOrg?.organizationName ?? 'your organization'}`}
      />

      <div className="flex gap-2">
        {STEPS.map((label, index) => (
          <div
            key={label}
            className={cn(
              'flex-1 rounded-lg px-3 py-2 text-center text-xs font-medium transition-colors',
              index === step
                ? 'bg-primary/10 text-primary'
                : index < step
                  ? 'text-foreground'
                  : 'text-muted-foreground',
            )}
          >
            {index + 1}. {label}
          </div>
        ))}
      </div>

      <div className="min-h-[320px] space-y-6 rounded-2xl bg-muted/20 p-6 ring-1 ring-border/30">
        {step === 0 && (
          <>
            <div className="space-y-2">
              <label htmlFor="game-name" className="text-sm font-medium">
                Game name
              </label>
              <Input
                id="game-name"
                placeholder="e.g. Aurora Fortune"
                value={name}
                onChange={(event) => setName(event.target.value)}
                className="text-lg"
              />
            </div>
            <div className="space-y-2">
              <p className="text-sm font-medium">Grid</p>
              <div className="grid grid-cols-2 gap-2">
                {GRID_OPTIONS.map((option) => (
                  <button
                    key={option.id}
                    type="button"
                    onClick={() => setGrid(option.id)}
                    className={cn(
                      'rounded-xl p-4 text-left transition-colors ring-1',
                      grid === option.id
                        ? 'bg-background ring-primary/50'
                        : 'bg-background/50 ring-border/40 hover:bg-background',
                    )}
                  >
                    <p className="text-lg font-semibold">{option.label}</p>
                    <p className="text-xs text-muted-foreground">{option.detail}</p>
                  </button>
                ))}
              </div>
            </div>
          </>
        )}

        {step === 1 && (
          <div className="space-y-3">
            <p className="text-sm font-medium">Features</p>
            <div className="flex flex-wrap gap-2">
              {FEATURE_OPTIONS.map((option) => {
                const active = features.includes(option.id)
                return (
                  <button
                    key={option.id}
                    type="button"
                    onClick={() => toggleFeature(option.id)}
                    className={cn(
                      'rounded-full px-4 py-2 text-sm font-medium transition-colors ring-1',
                      active
                        ? 'bg-primary text-primary-foreground ring-primary'
                        : 'bg-background ring-border/40 hover:ring-border',
                    )}
                  >
                    {option.label}
                  </button>
                )
              })}
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-5">
            <VisualMeter
              label="Target RTP"
              value={targetRtp}
              min={85}
              max={99}
              unit="%"
              onChange={setTargetRtp}
            />
            <VisualMeter
              label="Hit rate"
              value={hitRate}
              min={10}
              max={50}
              unit="%"
              onChange={setHitRate}
            />
            <VisualMeter
              label="Maximum win"
              value={maxWin}
              min={500}
              max={20000}
              unit="x"
              onChange={setMaxWin}
            />
            <div className="space-y-2">
              <p className="text-xs font-medium text-muted-foreground">Volatility</p>
              <div className="flex gap-1 rounded-lg bg-muted/50 p-1">
                {(['low', 'medium', 'high'] as Volatility[]).map((level) => (
                  <button
                    key={level}
                    type="button"
                    onClick={() => setVolatility(level)}
                    className={cn(
                      'flex-1 rounded-md px-2 py-1.5 text-xs font-medium capitalize transition-colors',
                      volatility === level
                        ? 'bg-background shadow-sm'
                        : 'text-muted-foreground',
                    )}
                  >
                    {level}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-4 text-center">
            <Sparkles className="mx-auto h-10 w-10 text-primary" />
            <div>
              <p className="text-xl font-semibold">{name || 'Untitled game'}</p>
              <p className="mt-2 text-sm text-muted-foreground">{buildDescription()}</p>
            </div>
            <p className="text-sm text-muted-foreground">
              We&apos;ll create your game shell. Open Studio to generate the initial reel design.
            </p>
            <Button
              type="button"
              size="lg"
              disabled={!name.trim() || createGame.isPending}
              onClick={handleCreate}
            >
              {createGame.isPending ? 'Creating…' : 'Create game'}
            </Button>
          </div>
        )}
      </div>

      <div className="flex items-center justify-between">
        <Button variant="ghost" asChild>
          <Link to="/games">Cancel</Link>
        </Button>
        <div className="flex gap-2">
          {step > 0 && step < 3 ? (
            <Button type="button" variant="outline" onClick={() => setStep((s) => s - 1)}>
              <ChevronLeft className="h-4 w-4" />
              Back
            </Button>
          ) : null}
          {step < 3 ? (
            <Button
              type="button"
              disabled={step === 0 && !name.trim()}
              onClick={() => setStep((s) => s + 1)}
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </Button>
          ) : null}
        </div>
      </div>
    </PageLayout>
  )
}
