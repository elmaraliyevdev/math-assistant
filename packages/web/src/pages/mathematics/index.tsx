import { useEffect, useState } from 'react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
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
import { useSearch } from '@tanstack/react-router'

type MathematicsTab = 'theoretical' | 'calibration' | 'certification'

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

  const [tab, setTab] = useState<MathematicsTab>('theoretical')
  const [gameId, setGameId] = useState(routeSearch.gameId ?? '')
  const [gameVersionId, setGameVersionId] = useState(routeSearch.gameVersionId ?? '')
  const [simulationId, setSimulationId] = useState(routeSearch.simulationId ?? '')
  const [simulatedRtp, setSimulatedRtp] = useState('')

  useEffect(() => {
    if (routeSearch.gameId) setGameId(routeSearch.gameId)
    if (routeSearch.gameVersionId) setGameVersionId(routeSearch.gameVersionId)
    if (routeSearch.simulationId) {
      setSimulationId(routeSearch.simulationId)
      setTab('calibration')
    }
  }, [routeSearch.gameId, routeSearch.gameVersionId, routeSearch.simulationId])

  const versions = useGameVersions(gameId)

  const requestBody = {
    gameVersionId,
    simulationId: simulationId || undefined,
    simulatedRtp: simulatedRtp ? Number(simulatedRtp) : undefined,
  }

  const canRun = Boolean(gameVersionId)

  const handleRun = () => {
    if (!canRun) return
    if (tab === 'theoretical') {
      theoretical.mutate({ gameVersionId })
      return
    }
    if (tab === 'calibration') {
      calibrate.mutate(requestBody)
      return
    }
    certification.mutate(requestBody)
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

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Mathematics Workbench</h1>
        <p className="text-sm text-muted-foreground">
          Compare theoretical game mathematics against simulation results and generate
          calibration recommendations.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Configuration</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <div className="space-y-2">
            <Label>Game</Label>
            <Select
              value={gameId}
              onValueChange={(value) => {
                setGameId(value)
                setGameVersionId('')
              }}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select game" />
              </SelectTrigger>
              <SelectContent>
                {(games.data?.items ?? []).map((game) => (
                  <SelectItem key={game.id} value={game.id}>
                    {game.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Game version</Label>
            <Select
              value={gameVersionId}
              onValueChange={setGameVersionId}
              disabled={!gameId}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select version" />
              </SelectTrigger>
              <SelectContent>
                {(versions.data ?? []).map((version) => (
                  <SelectItem key={version.id} value={version.id}>
                    v{version.version}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {tab !== 'theoretical' && (
            <>
              <div className="space-y-2">
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

              <div className="space-y-2">
                <Label>Simulated RTP override</Label>
                <Input
                  placeholder="e.g. 0.96"
                  value={simulatedRtp}
                  onChange={(event) => setSimulatedRtp(event.target.value)}
                />
              </div>
            </>
          )}
        </CardContent>
      </Card>

      <div className="flex flex-wrap gap-2">
        {(['theoretical', 'calibration', 'certification'] as const).map((value) => (
          <Button
            key={value}
            variant={tab === value ? 'default' : 'outline'}
            onClick={() => setTab(value)}
          >
            {value === 'theoretical'
              ? 'Theoretical RTP'
              : value === 'calibration'
                ? 'Calibration'
                : 'Certification'}
          </Button>
        ))}
        <Button className="ml-auto" disabled={!canRun || loading} onClick={handleRun}>
          {loading ? 'Running…' : 'Run analysis'}
        </Button>
      </div>

      {tab === 'theoretical' && theoretical.data && (
        <TheoreticalRtpPanel data={theoretical.data} />
      )}
      {tab === 'calibration' && calibrate.data && (
        <CalibrationDashboard data={calibrate.data} />
      )}
      {tab === 'certification' && certification.data && (
        <CertificationReportViewer
          report={certification.data}
          downloading={downloadReport.isPending}
          onDownload={handleDownload}
        />
      )}
    </div>
  )
}
