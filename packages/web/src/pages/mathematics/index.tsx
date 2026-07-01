import { useEffect, useMemo, useState } from 'react'
import { useSearch } from '@tanstack/react-router'
import {
  Activity,
  BarChart3,
  CheckCircle2,
  Gauge,
  LineChart,
  ShieldCheck,
  Sparkles,
} from 'lucide-react'

import { PageHeader, PageLayout } from '@/components/design-system'
import { EmptyState } from '@/components/design-system'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { CalibrationDashboard } from '@/features/mathematics/components/CalibrationDashboard'
import { CertificationReportViewer } from '@/features/mathematics/components/CertificationReportViewer'
import { TheoreticalRtpPanel } from '@/features/mathematics/components/TheoreticalRtpPanel'
import {
  useCalibrateMathematics,
  useCertificationReport,
  useDownloadCertificationReport,
  useTheoreticalAnalysis,
} from '@/features/mathematics/hooks/use-mathematics'
import { useGames, useGameVersions } from '@/features/games/hooks/use-games'
import { useSimulations } from '@/features/simulations/hooks/use-simulations'
import { AiHelpLink } from '@/features/settings/components/settings-primitives'
import { cn } from '@/lib/utils'

type AnalysisType =
  | 'theoretical'
  | 'calibration'
  | 'certification'
  | 'volatility'
  | 'hit-frequency'
  | 'feature-analysis'

const ANALYSIS_OPTIONS: Array<{
  id: AnalysisType
  title: string
  description: string
  icon: typeof Gauge
  available: boolean
}> = [
  {
    id: 'theoretical',
    title: 'Theoretical RTP',
    description: 'Compute math model RTP from canonical JSON.',
    icon: Gauge,
    available: true,
  },
  {
    id: 'calibration',
    title: 'Calibration',
    description: 'Compare simulation results against theoretical targets.',
    icon: LineChart,
    available: true,
  },
  {
    id: 'certification',
    title: 'Certification',
    description: 'Generate certification-ready validation report.',
    icon: ShieldCheck,
    available: true,
  },
  {
    id: 'volatility',
    title: 'Volatility',
    description: 'Estimate variance profile and hit distribution.',
    icon: Activity,
    available: false,
  },
  {
    id: 'hit-frequency',
    title: 'Hit Frequency',
    description: 'Analyze win rate and dead-spin intervals.',
    icon: BarChart3,
    available: false,
  },
  {
    id: 'feature-analysis',
    title: 'Feature Analysis',
    description: 'Break down bonus contribution and trigger rates.',
    icon: Sparkles,
    available: false,
  },
]

const PRESETS_KEY = 'ma_math_presets'

interface MathPreset {
  id: string
  name: string
  gameId: string
  gameVersionId: string
  analysis: AnalysisType
}

function loadPresets(): MathPreset[] {
  try {
    const raw = localStorage.getItem(PRESETS_KEY)
    return raw ? (JSON.parse(raw) as MathPreset[]) : []
  } catch {
    return []
  }
}

function savePreset(preset: MathPreset) {
  const current = loadPresets().filter((entry) => entry.id !== preset.id)
  localStorage.setItem(PRESETS_KEY, JSON.stringify([preset, ...current].slice(0, 6)))
}

export function MathematicsPage() {
  const routeSearch = useSearch({ strict: false }) as {
    gameId?: string
    gameVersionId?: string
    simulationId?: string
  }
  const games = useGames()
  const simulations = useSimulations({ page: 1, pageSize: 50, status: 'completed' })
  const theoretical = useTheoreticalAnalysis()
  const calibrate = useCalibrateMathematics()
  const certification = useCertificationReport()
  const downloadReport = useDownloadCertificationReport()

  const [step, setStep] = useState<1 | 2 | 3>(1)
  const [analysis, setAnalysis] = useState<AnalysisType>('theoretical')
  const [gameId, setGameId] = useState(routeSearch.gameId ?? '')
  const [gameVersionId, setGameVersionId] = useState(routeSearch.gameVersionId ?? '')
  const [simulationId, setSimulationId] = useState(routeSearch.simulationId ?? '')
  const [simulatedRtp, setSimulatedRtp] = useState('')
  const [presets, setPresets] = useState(loadPresets)
  const [hasRun, setHasRun] = useState(false)

  useEffect(() => {
    if (routeSearch.gameId) {
      setGameId(routeSearch.gameId)
      setStep(2)
    }
    if (routeSearch.gameVersionId) {
      setGameVersionId(routeSearch.gameVersionId)
      setStep(3)
    }
    if (routeSearch.simulationId) {
      setSimulationId(routeSearch.simulationId)
      setAnalysis('calibration')
    }
  }, [routeSearch.gameId, routeSearch.gameVersionId, routeSearch.simulationId])

  const versions = useGameVersions(gameId)

  const requestBody = {
    gameVersionId,
    simulationId: simulationId || undefined,
    simulatedRtp: simulatedRtp ? Number(simulatedRtp) : undefined,
  }

  const canRun = Boolean(gameVersionId) && ANALYSIS_OPTIONS.find((o) => o.id === analysis)?.available

  const handleRun = () => {
    if (!canRun) return
    setHasRun(true)
    if (analysis === 'theoretical') {
      theoretical.mutate({ gameVersionId })
      return
    }
    if (analysis === 'calibration') {
      calibrate.mutate(requestBody)
      return
    }
    if (analysis === 'certification') {
      certification.mutate(requestBody)
    }
  }

  const handleDownload = async (format: 'json' | 'pdf') => {
    if (!gameVersionId) return
    const blob = await downloadReport.mutateAsync({
      body: requestBody,
      format,
    })
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = `certification-${gameVersionId}.${format}`
    anchor.click()
    URL.revokeObjectURL(url)
  }

  const loading =
    theoretical.isPending || calibrate.isPending || certification.isPending

  const filteredSimulations =
    simulations.data?.items.filter(
      (item) => !gameVersionId || item.gameVersionId === gameVersionId,
    ) ?? []

  const selectedGameName = useMemo(
    () => games.data?.items.find((game) => game.id === gameId)?.name,
    [gameId, games.data?.items],
  )

  const selectedVersion = useMemo(
    () => versions.data?.find((version) => version.id === gameVersionId),
    [gameVersionId, versions.data],
  )

  const saveCurrentPreset = () => {
    if (!gameId || !gameVersionId) return
    const preset: MathPreset = {
      id: `${gameVersionId}-${analysis}`,
      name: `${selectedGameName ?? 'Game'} · ${analysis}`,
      gameId,
      gameVersionId,
      analysis,
    }
    savePreset(preset)
    setPresets(loadPresets())
  }

  const showResults =
    hasRun &&
    ((analysis === 'theoretical' && theoretical.data) ||
      (analysis === 'calibration' && calibrate.data) ||
      (analysis === 'certification' && certification.data))

  return (
    <PageLayout className="space-y-4">
      <PageHeader
        title="Mathematics Workbench"
        description="Guided analysis from game selection through certification."
        className="mb-4"
        actions={<AiHelpLink prompt="Explain certification requirements for a 96% RTP slot" />}
      />

      <div className="grid gap-3 lg:grid-cols-3">
        <WizardStep
          step={1}
          title="Select game"
          active={step === 1}
          complete={Boolean(gameId)}
          onClick={() => setStep(1)}
        >
          <Select
            value={gameId}
            onValueChange={(value) => {
              setGameId(value)
              setGameVersionId('')
              setStep(2)
              setHasRun(false)
            }}
          >
            <SelectTrigger>
              <SelectValue placeholder="Choose a game" />
            </SelectTrigger>
            <SelectContent>
              {(games.data?.items ?? []).map((game) => (
                <SelectItem key={game.id} value={game.id}>
                  {game.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </WizardStep>

        <WizardStep
          step={2}
          title="Select version"
          active={step === 2}
          complete={Boolean(gameVersionId)}
          disabled={!gameId}
          onClick={() => gameId && setStep(2)}
        >
          <Select
            value={gameVersionId}
            onValueChange={(value) => {
              setGameVersionId(value)
              setStep(3)
              setHasRun(false)
            }}
            disabled={!gameId}
          >
            <SelectTrigger>
              <SelectValue placeholder="Choose version" />
            </SelectTrigger>
            <SelectContent>
              {(versions.data ?? []).map((version) => (
                <SelectItem key={version.id} value={version.id}>
                  v{version.version}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </WizardStep>

        <WizardStep
          step={3}
          title="Choose analysis"
          active={step === 3}
          complete={Boolean(analysis)}
          disabled={!gameVersionId}
          onClick={() => gameVersionId && setStep(3)}
        >
          <p className="text-xs text-muted-foreground">
            {selectedGameName ?? 'Game'} · v{selectedVersion?.version ?? '—'}
          </p>
        </WizardStep>
      </div>

      {!gameId ? (
        <EmptyState
          title="Select a game to begin analysis"
          description="Pick a game and version, then choose the mathematics workflow you need."
        />
      ) : (
        <>
          {step === 3 ? (
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {ANALYSIS_OPTIONS.map((option) => {
                const Icon = option.icon
                const selected = analysis === option.id
                return (
                  <button
                    key={option.id}
                    type="button"
                    disabled={!option.available}
                    onClick={() => {
                      setAnalysis(option.id)
                      setHasRun(false)
                    }}
                    className={cn(
                      'rounded-lg border p-3 text-left transition-colors',
                      selected ? 'border-primary bg-primary/5' : 'hover:bg-muted/40',
                      !option.available && 'opacity-60',
                    )}
                  >
                    <div className="mb-2 flex items-center gap-2">
                      <Icon className="h-4 w-4 text-primary" />
                      <span className="text-sm font-medium">{option.title}</span>
                      {!option.available ? (
                        <Badge variant="outline" className="ml-auto text-[10px]">
                          Soon
                        </Badge>
                      ) : null}
                    </div>
                    <p className="text-xs text-muted-foreground">{option.description}</p>
                  </button>
                )
              })}
            </div>
          ) : null}

          {analysis !== 'theoretical' && gameVersionId ? (
            <Card>
              <CardContent className="grid gap-3 p-4 md:grid-cols-2">
                <div className="space-y-1.5">
                  <Label>Simulation (optional)</Label>
                  <Select value={simulationId} onValueChange={setSimulationId}>
                    <SelectTrigger>
                      <SelectValue placeholder="Link completed simulation" />
                    </SelectTrigger>
                    <SelectContent>
                      {filteredSimulations.map((simulation) => (
                        <SelectItem key={simulation.id} value={simulation.id}>
                          {simulation.id.slice(0, 8)} · {simulation.spinCount} spins
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1.5">
                  <Label>Simulated RTP override</Label>
                  <Input
                    placeholder="e.g. 0.96"
                    value={simulatedRtp}
                    onChange={(event) => setSimulatedRtp(event.target.value)}
                  />
                </div>
              </CardContent>
            </Card>
          ) : null}

          <div className="flex flex-wrap items-center gap-2">
            <Button disabled={!canRun || loading} onClick={handleRun}>
              {loading ? 'Running…' : 'Run analysis'}
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={!gameVersionId}
              onClick={saveCurrentPreset}
            >
              Save preset
            </Button>
            {presets.length ? (
              <Select
                onValueChange={(value) => {
                  const preset = presets.find((entry) => entry.id === value)
                  if (!preset) return
                  setGameId(preset.gameId)
                  setGameVersionId(preset.gameVersionId)
                  setAnalysis(preset.analysis)
                  setStep(3)
                }}
              >
                <SelectTrigger className="w-52">
                  <SelectValue placeholder="Load preset" />
                </SelectTrigger>
                <SelectContent>
                  {presets.map((preset) => (
                    <SelectItem key={preset.id} value={preset.id}>
                      {preset.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            ) : null}
          </div>
        </>
      )}

      {showResults ? (
        <div className="space-y-4 border-t pt-4">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-500" />
            <h2 className="text-lg font-semibold">Results dashboard</h2>
          </div>

          {analysis === 'theoretical' && theoretical.data ? (
            <TheoreticalRtpPanel data={theoretical.data} />
          ) : null}
          {analysis === 'calibration' && calibrate.data ? (
            <CalibrationDashboard data={calibrate.data} />
          ) : null}
          {analysis === 'certification' && certification.data ? (
            <CertificationReportViewer
              report={certification.data}
              downloading={downloadReport.isPending}
              onDownload={handleDownload}
            />
          ) : null}
        </div>
      ) : null}
    </PageLayout>
  )
}

function WizardStep({
  step,
  title,
  active,
  complete,
  disabled,
  children,
  onClick,
}: {
  step: number
  title: string
  active: boolean
  complete: boolean
  disabled?: boolean
  children: React.ReactNode
  onClick: () => void
}) {
  return (
    <Card
      className={cn(
        'transition-colors',
        active && 'border-primary/50',
        disabled && 'opacity-60',
      )}
    >
      <CardContent className="space-y-2 p-4">
        <button
          type="button"
          className="flex w-full items-center gap-2 text-left"
          onClick={onClick}
          disabled={disabled}
        >
          <span
            className={cn(
              'flex h-6 w-6 items-center justify-center rounded-full text-xs font-semibold',
              complete ? 'bg-primary text-primary-foreground' : 'bg-muted',
            )}
          >
            {step}
          </span>
          <span className="text-sm font-medium">{title}</span>
        </button>
        {children}
      </CardContent>
    </Card>
  )
}
