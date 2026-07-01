import { useCallback, useEffect, useState } from 'react'

import {
  createConversation,
  listConversations,
  saveConversations,
  titleFromMessage,
} from '@/features/assistant/lib/conversations'
import type {
  AssistantChatMessage,
  AssistantContextState,
  AssistantConversation,
} from '@/features/assistant/types'

export function useAssistantConversations() {
  const [conversations, setConversations] = useState<AssistantConversation[]>([])
  const [activeId, setActiveId] = useState<string | null>(null)

  useEffect(() => {
    const stored = listConversations()
    setConversations(stored)
    setActiveId(stored[0]?.id ?? null)
  }, [])

  const activeConversation =
    conversations.find((conversation) => conversation.id === activeId) ?? null

  const persist = useCallback((next: AssistantConversation[]) => {
    const saved = saveConversations(next)
    setConversations(saved)
    return saved
  }, [])

  const startNewChat = useCallback(
    (context?: AssistantContextState) => {
      const conversation = createConversation(context)
      const saved = persist([conversation, ...conversations])
      setActiveId(conversation.id)
      return saved.find((item) => item.id === conversation.id)!
    },
    [conversations, persist],
  )

  const updateConversation = useCallback(
    (id: string, updater: (conversation: AssistantConversation) => AssistantConversation) => {
      const next = conversations.map((conversation) =>
        conversation.id === id ? updater(conversation) : conversation,
      )
      persist(next)
    },
    [conversations, persist],
  )

  const appendMessage = useCallback(
    (id: string, message: AssistantChatMessage, userPromptForTitle?: string) => {
      updateConversation(id, (conversation) => {
        const title =
          conversation.messages.length === 0 && userPromptForTitle
            ? titleFromMessage(userPromptForTitle)
            : conversation.title
        return {
          ...conversation,
          title,
          updatedAt: new Date().toISOString(),
          messages: [...conversation.messages, message],
        }
      })
    },
    [updateConversation],
  )

  const patchMessage = useCallback(
    (conversationId: string, messageId: string, patch: Partial<AssistantChatMessage>) => {
      updateConversation(conversationId, (conversation) => ({
        ...conversation,
        updatedAt: new Date().toISOString(),
        messages: conversation.messages.map((message) =>
          message.id === messageId ? { ...message, ...patch } : message,
        ),
      }))
    },
    [updateConversation],
  )

  const setContext = useCallback(
    (id: string, context: AssistantContextState) => {
      updateConversation(id, (conversation) => ({
        ...conversation,
        context,
        updatedAt: new Date().toISOString(),
      }))
    },
    [updateConversation],
  )

  const deleteConversation = useCallback(
    (id: string) => {
      const next = conversations.filter((conversation) => conversation.id !== id)
      const saved = persist(next)
      if (activeId === id) {
        setActiveId(saved[0]?.id ?? null)
      }
    },
    [activeId, conversations, persist],
  )

  return {
    conversations,
    activeConversation,
    activeId,
    setActiveId,
    startNewChat,
    appendMessage,
    patchMessage,
    setContext,
    deleteConversation,
  }
}
