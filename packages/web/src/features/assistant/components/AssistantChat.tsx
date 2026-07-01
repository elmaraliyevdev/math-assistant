import { useEffect, useMemo, useState } from 'react'

import { AssistantAssistantBubble, AssistantUserBubble } from '@/features/assistant/components/AssistantMessage'
import { AssistantComposer } from '@/features/assistant/components/AssistantComposer'
import { AssistantContextChips } from '@/features/assistant/components/AssistantContextChips'
import { AssistantContextSidebar } from '@/features/assistant/components/AssistantContextSidebar'
import { AssistantHistorySidebar } from '@/features/assistant/components/AssistantHistorySidebar'
import { AssistantWelcome } from '@/features/assistant/components/AssistantWelcome'
import { revealText } from '@/features/assistant/lib/conversations'
import {
  isRecommendIntent,
  parseTargetRtp,
  toAssistantMessage,
} from '@/features/assistant/lib/intent'
import { followUpsForMode, resolveSlashCommand } from '@/features/assistant/lib/prompts'
import {
  useAnalyzeSimulation,
  useCompareSimulationsAssistant,
  useExplainGameVersion,
  useRecommendSimulation,
} from '@/features/assistant/hooks/use-assistant'
import { useAssistantConversations } from '@/features/assistant/hooks/use-assistant-conversations'
import type { AssistantContextState } from '@/features/assistant/types'
import { useGames, useGameVersions } from '@/features/games/hooks/use-games'
import { useGameVersionBySimulation } from '@/features/simulations/hooks/use-game-version-lookup'
import {
  useSimulationResults,
  useSimulations,
} from '@/features/simulations/hooks/use-simulations'
import { computeSimulationHealth } from '@/features/simulations/utils/health-score'

export function AssistantChat() {
  const games = useGames()
  const simulations = useSimulations({ page: 1, pageSize: 50, status: 'completed' })
  const {
    conversations,
    activeConversation,
    activeId,
    setActiveId,
    startNewChat,
    appendMessage,
    patchMessage,
    setContext,
    deleteConversation,
  } = useAssistantConversations()

  const analyze = useAnalyzeSimulation()
  const recommend = useRecommendSimulation()
  const compare = useCompareSimulationsAssistant()
  const explain = useExplainGameVersion()

  const [input, setInput] = useState('')

  const context = activeConversation?.context ?? {
    mode: 'simulation' as const,
    gameId: '',
    gameVersionId: '',
    simulationId: '',
    compareIds: [],
  }

  const versions = useGameVersions(context.gameId)
  const simulationMeta = useMemo(
    () =>
      (simulations.data?.items ?? []).find((item) => item.id === context.simulationId),
    [context.simulationId, simulations.data?.items],
  )
  const gameVersionLookup = useGameVersionBySimulation(simulationMeta?.gameVersionId)
  const simulationResults = useSimulationResults(
    context.simulationId,
    Boolean(context.simulationId),
  )

  const loading =
    analyze.isPending || recommend.isPending || compare.isPending || explain.isPending

  const completedSimulations = simulations.data?.items ?? []
  const gamesList = games.data?.items ?? []

  const selectedGame = gamesList.find((game) => game.id === context.gameId)
  const selectedVersion = (versions.data ?? []).find(
    (version) => version.id === context.gameVersionId,
  )

  const studioGameId = context.gameId || gameVersionLookup.gameId || ''
  const studioVersionId =
    context.gameVersionId || simulationMeta?.gameVersionId || ''

  const healthScore = simulationResults.data
    ? computeSimulationHealth(simulationResults.data).score
    : null
  const observedRtp = simulationResults.data?.summary.rtp ?? null
  const targetRtp = simulationResults.data?.rtpValidation?.targetRtp ?? null

  useEffect(() => {
    if (!activeConversation && conversations.length === 0) {
      startNewChat()
    }
  }, [activeConversation, conversations.length, startNewChat])

  const updateContext = (patch: Partial<AssistantContextState>) => {
    if (!activeId) return
    setContext(activeId, { ...context, ...patch })
  }

  const streamAssistantReply = async (
    conversationId: string,
    messageId: string,
    payload: ReturnType<typeof toAssistantMessage>,
    mode: AssistantContextState['mode'],
  ) => {
    const followUps = followUpsForMode(mode)
    patchMessage(conversationId, messageId, {
      ...payload,
      followUps,
      isStreaming: true,
      content: '',
    })

    await revealText(payload.content, (partial) => {
      patchMessage(conversationId, messageId, { content: partial, isStreaming: true })
    })

    patchMessage(conversationId, messageId, {
      content: payload.content,
      isStreaming: false,
      followUps,
    })
  }

  const handleSubmit = async (messageOverride?: string) => {
    const resolved = resolveSlashCommand(messageOverride ?? input) ?? (messageOverride ?? input)
    const trimmed = resolved.trim()
    if (!trimmed || loading || !activeId) return

    if (!messageOverride) setInput('')

    appendMessage(
      activeId,
      { id: crypto.randomUUID(), role: 'user', content: trimmed },
      trimmed,
    )

    const assistantId = crypto.randomUUID()
    appendMessage(activeId, {
      id: assistantId,
      role: 'assistant',
      content: '',
      isStreaming: true,
    })

    try {
      if (context.mode === 'simulation') {
        if (!context.simulationId) {
          patchMessage(activeId, assistantId, {
            content: 'Select a completed simulation in the context panel first.',
            isStreaming: false,
          })
          return
        }

        const response = isRecommendIntent(trimmed)
          ? await recommend.mutateAsync({
              simulationId: context.simulationId,
              targetRtp: parseTargetRtp(trimmed),
            })
          : await analyze.mutateAsync(context.simulationId)

        await streamAssistantReply(
          activeId,
          assistantId,
          toAssistantMessage(response),
          context.mode,
        )
        return
      }

      if (context.mode === 'compare') {
        if (context.compareIds.length < 2) {
          patchMessage(activeId, assistantId, {
            content: 'Select at least two simulations to compare.',
            isStreaming: false,
          })
          return
        }
        const response = await compare.mutateAsync(context.compareIds)
        await streamAssistantReply(
          activeId,
          assistantId,
          toAssistantMessage(response),
          context.mode,
        )
        return
      }

      if (!context.gameVersionId) {
        patchMessage(activeId, assistantId, {
          content: 'Select a game version in the context panel first.',
          isStreaming: false,
        })
        return
      }

      const response = await explain.mutateAsync(context.gameVersionId)
      await streamAssistantReply(
        activeId,
        assistantId,
        toAssistantMessage(response),
        context.mode,
      )
    } catch {
      patchMessage(activeId, assistantId, {
        content: 'Unable to generate a grounded response for that request.',
        isStreaming: false,
      })
    }
  }

  const messages = activeConversation?.messages ?? []
  const showWelcome = messages.length === 0

  return (
    <div className="grid h-full min-h-0 grid-cols-1 lg:grid-cols-[260px_minmax(0,1fr)_300px]">
      <div className="hidden lg:block">
        <AssistantHistorySidebar
          conversations={conversations}
          activeId={activeId}
          onSelect={setActiveId}
          onNew={() => startNewChat(context)}
          onDelete={deleteConversation}
        />
      </div>

      <section className="flex min-h-0 min-w-0 flex-col bg-background">
        <AssistantContextChips
          context={context}
          gameName={selectedGame?.name ?? gameVersionLookup.gameName}
          versionNumber={selectedVersion?.version ?? gameVersionLookup.versionNumber}
          healthScore={healthScore}
          targetRtp={targetRtp}
        />

        <div className="flex-1 overflow-y-auto">
          {showWelcome ? (
            <AssistantWelcome
              simulationLoaded={Boolean(context.simulationId && simulationResults.data)}
              healthScore={healthScore}
              observedRtp={observedRtp}
              targetRtp={targetRtp}
              onPrompt={(prompt) => void handleSubmit(prompt)}
            />
          ) : (
            <div className="mx-auto flex w-full max-w-3xl flex-col gap-4 px-4 py-6">
              {messages.map((message) =>
                message.role === 'user' ? (
                  <AssistantUserBubble key={message.id} content={message.content} />
                ) : (
                  <AssistantAssistantBubble
                    key={message.id}
                    message={message}
                    simulationId={context.simulationId || undefined}
                    gameVersionId={studioVersionId || undefined}
                    gameId={studioGameId || undefined}
                    onFollowUp={(prompt) => void handleSubmit(prompt)}
                  />
                ),
              )}
            </div>
          )}
        </div>

        <AssistantComposer
          value={input}
          onChange={setInput}
          onSubmit={() => void handleSubmit()}
          loading={loading}
          onQuickAction={(prompt) => void handleSubmit(prompt)}
          onUseContext={() => {
            if (context.mode === 'simulation' && context.simulationId) {
              void handleSubmit('Analyze the currently selected simulation.')
            } else if (context.mode === 'compare' && context.compareIds.length >= 2) {
              void handleSubmit('Compare the selected simulations.')
            } else if (context.gameVersionId) {
              void handleSubmit('Explain the selected game version design.')
            }
          }}
        />
      </section>

      <div className="hidden lg:block">
        <AssistantContextSidebar
          context={context}
          onChange={updateContext}
          games={gamesList}
          versions={versions.data ?? []}
          completedSimulations={completedSimulations}
          gameName={selectedGame?.name ?? gameVersionLookup.gameName}
          versionNumber={selectedVersion?.version ?? gameVersionLookup.versionNumber}
          observedRtp={observedRtp}
          targetRtp={targetRtp}
          healthScore={healthScore}
          certificationLabel={
            simulationResults.data?.certificationNotice ? 'Review notice' : null
          }
        />
      </div>
    </div>
  )
}
