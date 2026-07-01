import type { AssistantContextState, AssistantConversation } from '@/features/assistant/types'
import { DEFAULT_CONTEXT } from '@/features/assistant/types'

const STORAGE_KEY = 'math-assistant-conversations'
const MAX_CONVERSATIONS = 40

export function listConversations(): AssistantConversation[] {
  if (typeof window === 'undefined') return []
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw) as AssistantConversation[]
    return parsed.sort(
      (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime(),
    )
  } catch {
    return []
  }
}

export function saveConversations(conversations: AssistantConversation[]) {
  const trimmed = conversations
    .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
    .slice(0, MAX_CONVERSATIONS)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed))
  return trimmed
}

export function createConversation(context: AssistantContextState = DEFAULT_CONTEXT) {
  const now = new Date().toISOString()
  return {
    id: crypto.randomUUID(),
    title: 'New chat',
    createdAt: now,
    updatedAt: now,
    context: { ...context },
    messages: [],
  } satisfies AssistantConversation
}

export function titleFromMessage(message: string) {
  const cleaned = message.replace(/^\//, '').trim()
  if (!cleaned) return 'New chat'
  return cleaned.length > 42 ? `${cleaned.slice(0, 42)}…` : cleaned
}

export async function revealText(
  text: string,
  onUpdate: (value: string) => void,
  chunkDelayMs = 10,
) {
  const tokens = text.match(/\S+\s*/g) ?? [text]
  let current = ''
  for (const token of tokens) {
    current += token
    onUpdate(current)
    await new Promise((resolve) => setTimeout(resolve, chunkDelayMs))
  }
}
