import { Link, useNavigate } from '@tanstack/react-router'
import { useState } from 'react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useMe } from '@/features/auth/use-auth'
import { GameForm } from '@/features/games/components'
import { DEFAULT_ENGINE_VERSION } from '@/features/games/schemas/game-schemas'
import { useCreateGame, useCreateGameVersion } from '@/features/games/hooks/use-games'
import { OnboardingProgressHeader } from '@/features/onboarding/components/OnboardingProgressHeader'
import {
  ONBOARDING_SAMPLE_JSON,
  ONBOARDING_SPIN_COUNT,
  setOnboardingCompleted,
  type OnboardingStep,
} from '@/features/onboarding/storage'
import { SimulationForm } from '@/features/simulations/components'
import { SimulationLimitsNotice } from '@/features/simulations/components/SimulationLimitsNotice'
import { useCreateSimulation, useSimulation } from '@/features/simulations/hooks/use-simulations'
import { evaluateSimulationLimits } from '@/features/simulations/hooks/use-simulation-limits'
import { useEngineVersion } from '@/features/simulations/hooks/use-engine'
import {
  useCreateOrganization,
  useOrganizations,
} from '@/features/organizations/use-organizations'
import { useOrganizationStore } from '@/stores/organization-store'

export function OnboardingPage() {
  const navigate = useNavigate()
  const { data: me } = useMe()
  const organizations = useOrganizations()
  const createOrganization = useCreateOrganization()
  const organizationId = useOrganizationStore((state) => state.currentOrganizationId)

  const [step, setStep] = useState<OnboardingStep>('welcome')
  const [orgName, setOrgName] = useState('')
  const [orgSlug, setOrgSlug] = useState('')
  const [gameId, setGameId] = useState<string | null>(null)
  const [gameName, setGameName] = useState('')
  const [versionId, setVersionId] = useState<string | null>(null)
  const [jsonText, setJsonText] = useState(ONBOARDING_SAMPLE_JSON)
  const [simulationId, setSimulationId] = useState<string | null>(null)

  const createGame = useCreateGame({ suppressNavigation: true })
  const createVersion = useCreateGameVersion(gameId ?? '', { suppressNavigation: true })
  const createSimulation = useCreateSimulation({ suppressNavigation: true })
  const engine = useEngineVersion()

  const simulation = useSimulation(simulationId ?? '', true)

  async function finishOnboarding() {
    setOnboardingCompleted()
    await navigate({ to: '/dashboard' })
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Getting started</h2>
        <p className="text-muted-foreground">
          Complete these steps to run your first certified simulation.
        </p>
      </div>

      <OnboardingProgressHeader step={step} />

      {step === 'welcome' && (
        <Card>
          <CardHeader>
            <CardTitle>Welcome to Math Assistant</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              This guided setup walks you through creating a workspace, uploading a game
              version, and running a 100,000-spin simulation. Estimated total time: ~12
              minutes.
            </p>
            <div className="flex flex-wrap gap-2">
              <Button onClick={() => setStep('organization')}>Get started</Button>
              <Button variant="outline" asChild>
                <Link to="/templates">Browse game templates</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {step === 'organization' && (
        <Card>
          <CardHeader>
            <CardTitle>Create or confirm your organization</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {me?.organizations.length ? (
              <p className="text-sm text-muted-foreground">
                You are already in{' '}
                <span className="font-medium text-foreground">
                  {me.organizations[0].organizationName}
                </span>
                . Continue to create your first game.
              </p>
            ) : (
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="onboarding-org-name">Organization name</Label>
                  <Input
                    id="onboarding-org-name"
                    value={orgName}
                    onChange={(event) => setOrgName(event.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="onboarding-org-slug">Slug</Label>
                  <Input
                    id="onboarding-org-slug"
                    value={orgSlug}
                    onChange={(event) => setOrgSlug(event.target.value)}
                  />
                </div>
              </div>
            )}
            <div className="flex gap-2">
              <Button
                onClick={async () => {
                  if (!me?.organizations.length) {
                    const org = await createOrganization.mutateAsync({
                      name: orgName,
                      slug: orgSlug,
                    })
                    useOrganizationStore.getState().setCurrentOrganizationId(org.id)
                  }
                  setStep('game')
                }}
                disabled={
                  createOrganization.isPending ||
                  organizations.isLoading ||
                  (!me?.organizations.length && (!orgName || !orgSlug))
                }
              >
                Continue
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {step === 'game' && (
        <Card>
          <CardHeader>
            <CardTitle>Create your first game</CardTitle>
          </CardHeader>
          <CardContent>
            <GameForm
              submitLabel="Create game and continue"
              loading={createGame.isPending}
              onSubmit={async (values) => {
                if (!organizationId) return
                const game = await createGame.mutateAsync({
                  ...values,
                  organizationId,
                })
                setGameId(game.id)
                setGameName(game.name)
                setStep('version')
              }}
            />
          </CardContent>
        </Card>
      )}

      {step === 'version' && gameId && (
        <Card>
          <CardHeader>
            <CardTitle>Upload a game version</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Paste canonical JSON for <span className="font-medium">{gameName}</span>, or{' '}
              <Link to="/templates" className="font-medium text-primary underline-offset-4 hover:underline">
                start from a template
              </Link>{' '}
              and import its JSON here.
            </p>
            <Textarea
              rows={10}
              value={jsonText}
              onChange={(event) => setJsonText(event.target.value)}
            />
            <Button
              disabled={createVersion.isPending}
              onClick={async () => {
                const version = await createVersion.mutateAsync({
                  canonicalJson: JSON.parse(jsonText) as Record<string, unknown>,
                  engineVersion: engine.data?.engineVersion ?? DEFAULT_ENGINE_VERSION,
                })
                setVersionId(version.id)
                setStep('simulation')
              }}
            >
              Upload version and continue
            </Button>
          </CardContent>
        </Card>
      )}

      {step === 'simulation' && gameId && versionId && (
        <Card>
          <CardHeader>
            <CardTitle>Run your first simulation</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <SimulationLimitsNotice spinCount={ONBOARDING_SPIN_COUNT} />
            <SimulationForm
              games={[{ id: gameId, name: gameName, organizationId: organizationId ?? '', description: null, createdAt: '', updatedAt: '' }]}
              defaultValues={{
                gameId,
                gameVersionId: versionId,
                spinCount: ONBOARDING_SPIN_COUNT,
                betMinorUnits: 100,
                eventLogMode: 'none',
              }}
              submitLabel="Start 100K-spin simulation"
              loading={createSimulation.isPending}
              onSubmit={async (values) => {
                const limits = evaluateSimulationLimits(
                  values.spinCount,
                  engine.data,
                )
                if (limits.spinCountExceeded || limits.activeLimitReached) {
                  return
                }
                const result = await createSimulation.mutateAsync({
                  gameVersionId: values.gameVersionId,
                  spinCount: values.spinCount,
                  betMinorUnits: values.betMinorUnits,
                  eventLogMode: values.eventLogMode,
                })
                setSimulationId(result.simulationId)
                setStep('results')
              }}
            />
          </CardContent>
        </Card>
      )}

      {step === 'results' && simulationId && (
        <Card>
          <CardHeader>
            <CardTitle>Simulation results</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Status:{' '}
              <span className="font-medium capitalize text-foreground">
                {simulation.data?.status ?? 'pending'}
              </span>
            </p>
            {simulation.data?.status === 'completed' ? (
              <p className="text-sm text-muted-foreground">
                Your first simulation finished. Open the detail page to review certified
                metrics.
              </p>
            ) : (
              <p className="text-sm text-muted-foreground">
                Your simulation is running. This page refreshes automatically.
              </p>
            )}
            <div className="flex flex-wrap gap-2">
              <Button asChild variant="outline">
                <Link
                  to="/simulations/$simulationId"
                  params={{ simulationId }}
                >
                  View simulation
                </Link>
              </Button>
              <Button onClick={() => void finishOnboarding()}>
                Finish onboarding
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
