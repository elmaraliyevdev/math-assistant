import { useMemo, useState } from 'react'
import { Link } from '@tanstack/react-router'

import { Button } from '@/components/ui/button'
import { EmptyState } from '@/components/empty-state'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { CitationPanel } from '@/features/assistant/components/CitationPanel'
import {
  useAnalyzeSimulation,
  useCompareSimulationsAssistant,
  useExplainGameVersion,
  useRecommendSimulation,
} from '@/features/assistant/hooks/use-assistant'
import { useGames, useGameVersions } from '@/features/games/hooks/use-games'
import { useSimulations } from '@/features/simulations/hooks/use-simulations'
import type { GroundedCitation } from '@/types/api'

type ChatRole = 'user' | 'assistant'
type AssistantMode = 'simulation' | 'compare' | 'game-version'

interface ChatMessage {
  id: string
  role: ChatRole
  content: string
  citations?: GroundedCitation[]
}

function parseTargetRtp(message: string): number | undefined {
  const match = message.match(/(\d{1,3}(?:\.\d+)?)\s*%?/)
  if (!match) return undefined
  const value = Number(match[1])
  return Number.isFinite(value) ? value : undefined
}

export function AssistantChat() {
  const games = useGames()
  const simulations = useSimulations({ page: 1, pageSize: 50, status: 'completed' })

  const analyze = useAnalyzeSimulation()
  const recommend = useRecommendSimulation()
  const compare = useCompareSimulationsAssistant()
  const explain = useExplainGameVersion()

  const [mode, setMode] = useState<AssistantMode>('simulation')
  const [gameId, setGameId] = useState('')
  const [gameVersionId, setGameVersionId] = useState('')
  const [simulationId, setSimulationId] = useState('')
  const [compareIds, setCompareIds] = useState<string[]>([])
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content:
        'Ask about simulation results, game versions, RTP tuning, or comparison trade-offs. ' +
        'All answers are grounded in stored mathematics artifacts with citations.',
    },
  ])

  const versions = useGameVersions(gameId)
  const loading =
    analyze.isPending || recommend.isPending || compare.isPending || explain.isPending

  const completedSimulations = useMemo(
    () => simulations.data?.items ?? [],
    [simulations.data?.items],
  )

  const gamesList = games.data?.items ?? []
  const needsGames = mode === 'game-version' && gamesList.length === 0
  const needsSimulations =
    (mode === 'simulation' || mode === 'compare') && completedSimulations.length === 0

  const pushMessage = (message: ChatMessage) => {
    setMessages((current) => [...current, message])
  }

  const handleAssistantResponse = (content: string, citations: GroundedCitation[]) => {
    pushMessage({
      id: crypto.randomUUID(),
      role: 'assistant',
      content,
      citations,
    })
  }

  const runSimulationIntent = async (message: string) => {
    if (!simulationId) {
      pushMessage({
        id: crypto.randomUUID(),
        role: 'assistant',
        content: 'Select a completed simulation before asking simulation questions.',
      })
      return
    }

    const lower = message.toLowerCase()
    if (lower.includes('recommend') || lower.includes('tuning') || lower.includes('calibrat')) {
      const targetRtp = parseTargetRtp(message)
      const response = await recommend.mutateAsync({ simulationId, targetRtp })
      handleAssistantResponse(response.content, response.citations)
      return
    }

    const response = await analyze.mutateAsync(simulationId)
    handleAssistantResponse(response.content, response.citations)
  }

  const runCompareIntent = async () => {
    if (compareIds.length < 2) {
      pushMessage({
        id: crypto.randomUUID(),
        role: 'assistant',
        content: 'Select at least two completed simulations to compare.',
      })
      return
    }
    const response = await compare.mutateAsync(compareIds)
    handleAssistantResponse(response.content, response.citations)
  }

  const runGameVersionIntent = async () => {
    if (!gameVersionId) {
      pushMessage({
        id: crypto.randomUUID(),
        role: 'assistant',
        content: 'Select a game version before asking design questions.',
      })
      return
    }
    const response = await explain.mutateAsync(gameVersionId)
    handleAssistantResponse(response.content, response.citations)
  }

  const handleSubmit = async (messageOverride?: string) => {
    const trimmed = (messageOverride ?? input).trim()
    if (!trimmed || loading) return

    if (!messageOverride) {
      setInput('')
    }

    pushMessage({ id: crypto.randomUUID(), role: 'user', content: trimmed })

    try {
      if (mode === 'simulation') {
        await runSimulationIntent(trimmed)
      } else if (mode === 'compare') {
        await runCompareIntent()
      } else {
        await runGameVersionIntent()
      }
    } catch {
      pushMessage({
        id: crypto.randomUUID(),
        role: 'assistant',
        content: 'Unable to generate a grounded response for that request.',
      })
    }
  }

  const toggleCompareId = (id: string) => {
    setCompareIds((current) =>
      current.includes(id) ? current.filter((item) => item !== id) : [...current, id].slice(0, 5),
    )
  }

  return (
    <div className="grid gap-4 lg:grid-cols-[320px_1fr]">
      <Card>
        <CardHeader>
          <CardTitle>Context</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Assistant mode</Label>
            <Select value={mode} onValueChange={(value) => setMode(value as AssistantMode)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="simulation">Simulation analysis</SelectItem>
                <SelectItem value="compare">Simulation comparison</SelectItem>
                <SelectItem value="game-version">Game version design</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {needsGames && (
            <EmptyState
              title="No games available"
              description="Create a game and upload a version before asking the assistant about mathematical design."
              actions={
                <>
                  <Button size="sm" asChild>
                    <Link to="/games/create">Create game</Link>
                  </Button>
                  <Button size="sm" variant="outline" asChild>
                    <Link to="/templates">Browse templates</Link>
                  </Button>
                </>
              }
            />
          )}

          {needsSimulations && (
            <EmptyState
              title="No completed simulations"
              description="Run a simulation to completion, then return here to analyze results or compare runs."
              actions={
                <>
                  <Button size="sm" asChild>
                    <Link to="/simulations/create">Create simulation</Link>
                  </Button>
                  <Button size="sm" variant="outline" asChild>
                    <Link to="/simulations">View simulations</Link>
                  </Button>
                </>
              }
            />
          )}

          {mode === 'game-version' && !needsGames && (
            <>
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
                <Select value={gameVersionId} onValueChange={setGameVersionId}>
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
            </>
          )}

          {mode === 'simulation' && !needsSimulations && (
            <div className="space-y-2">
              <Label>Simulation</Label>
              <Select value={simulationId} onValueChange={setSimulationId}>
                <SelectTrigger>
                  <SelectValue placeholder="Select simulation" />
                </SelectTrigger>
                <SelectContent>
                  {completedSimulations.map((simulation) => (
                    <SelectItem key={simulation.id} value={simulation.id}>
                      {simulation.id.slice(0, 8)} · {simulation.spinCount} spins
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}

          {mode === 'compare' && !needsSimulations && (
            <div className="space-y-2">
              <Label>Simulations to compare</Label>
              <div className="max-h-48 space-y-2 overflow-y-auto rounded-md border p-2">
                {completedSimulations.map((simulation) => (
                  <label
                    key={simulation.id}
                    className="flex items-center gap-2 text-sm"
                  >
                    <input
                      type="checkbox"
                      checked={compareIds.includes(simulation.id)}
                      onChange={() => toggleCompareId(simulation.id)}
                    />
                    {simulation.id.slice(0, 8)} · {simulation.spinCount} spins
                  </label>
                ))}
              </div>
            </div>
          )}

          <div className="flex flex-wrap gap-2">
            {mode === 'simulation' && (
              <>
                <Button
                  size="sm"
                  variant="outline"
                  disabled={!simulationId || loading}
                  onClick={() => void handleSubmit('Explain RTP decomposition and feature contribution.')}
                >
                  Analyze RTP
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  disabled={!simulationId || loading}
                  onClick={() => void handleSubmit('Recommend RTP tuning actions for target 96%.')}
                >
                  Recommend tuning
                </Button>
              </>
            )}
            {mode === 'compare' && (
              <Button
                size="sm"
                variant="outline"
                disabled={compareIds.length < 2 || loading}
                onClick={() => void handleSubmit('Explain why RTP differs between these simulations.')}
              >
                Explain comparison
              </Button>
            )}
            {mode === 'game-version' && (
              <Button
                size="sm"
                variant="outline"
                disabled={!gameVersionId || loading}
                onClick={() => void handleSubmit('Summarize feature structure and risk profile.')}
              >
                Explain design
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      <Card className="flex min-h-[560px] flex-col">
        <CardHeader>
          <CardTitle>Mathematics Assistant</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-1 flex-col gap-4">
          <div className="flex-1 space-y-4 overflow-y-auto rounded-md border p-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={
                  message.role === 'user'
                    ? 'ml-8 rounded-md bg-primary/10 p-3 text-sm'
                    : 'mr-8 rounded-md bg-muted/40 p-3 text-sm'
                }
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
                {message.citations && message.citations.length > 0 && (
                  <div className="mt-3">
                    <CitationPanel citations={message.citations} />
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="space-y-2">
            <Textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask about RTP behavior, feature contribution, calibration, or comparisons..."
              rows={3}
            />
            <div className="flex justify-end">
              <Button disabled={loading || !input.trim()} onClick={() => void handleSubmit()}>
                {loading ? 'Thinking…' : 'Send'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
