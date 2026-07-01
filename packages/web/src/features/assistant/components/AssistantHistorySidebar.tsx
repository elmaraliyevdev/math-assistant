import { MessageSquarePlus, Trash2 } from 'lucide-react'

import { Button } from '@/components/ui/button'
import type { AssistantConversation } from '@/features/assistant/types'
import { cn } from '@/lib/utils'

function groupConversations(conversations: AssistantConversation[]) {
  const now = new Date()
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime()
  const startOfWeek = startOfToday - 6 * 86_400_000

  const today: AssistantConversation[] = []
  const week: AssistantConversation[] = []
  const older: AssistantConversation[] = []

  for (const conversation of conversations) {
    const time = new Date(conversation.updatedAt).getTime()
    if (time >= startOfToday) today.push(conversation)
    else if (time >= startOfWeek) week.push(conversation)
    else older.push(conversation)
  }

  return { today, week, older }
}

export function AssistantHistorySidebar({
  conversations,
  activeId,
  onSelect,
  onNew,
  onDelete,
}: {
  conversations: AssistantConversation[]
  activeId: string | null
  onSelect: (id: string) => void
  onNew: () => void
  onDelete: (id: string) => void
}) {
  const groups = groupConversations(conversations)

  return (
    <aside className="flex h-full min-h-0 flex-col border-r border-border/40 bg-muted/10">
      <div className="border-b border-border/40 p-3">
        <Button className="w-full justify-start gap-2" size="sm" onClick={onNew}>
          <MessageSquarePlus className="h-4 w-4" />
          New chat
        </Button>
      </div>
      <div className="flex-1 overflow-y-auto p-2">
        <ConversationGroup
          label="Today"
          conversations={groups.today}
          activeId={activeId}
          onSelect={onSelect}
          onDelete={onDelete}
        />
        <ConversationGroup
          label="This week"
          conversations={groups.week}
          activeId={activeId}
          onSelect={onSelect}
          onDelete={onDelete}
        />
        <ConversationGroup
          label="Earlier"
          conversations={groups.older}
          activeId={activeId}
          onSelect={onSelect}
          onDelete={onDelete}
        />
        {conversations.length === 0 && (
          <p className="px-2 py-6 text-center text-xs text-muted-foreground">
            No conversations yet
          </p>
        )}
      </div>
    </aside>
  )
}

function ConversationGroup({
  label,
  conversations,
  activeId,
  onSelect,
  onDelete,
}: {
  label: string
  conversations: AssistantConversation[]
  activeId: string | null
  onSelect: (id: string) => void
  onDelete: (id: string) => void
}) {
  if (conversations.length === 0) return null

  return (
    <div className="mb-4">
      <p className="px-2 pb-1 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
        {label}
      </p>
      <div className="space-y-0.5">
        {conversations.map((conversation) => (
          <div
            key={conversation.id}
            className={cn(
              'group flex items-center gap-1 rounded-lg',
              activeId === conversation.id && 'bg-background shadow-sm',
            )}
          >
            <button
              type="button"
              onClick={() => onSelect(conversation.id)}
              className="min-w-0 flex-1 truncate px-3 py-2 text-left text-sm hover:bg-muted/40"
            >
              {conversation.title}
            </button>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="mr-1 h-7 w-7 shrink-0 opacity-0 group-hover:opacity-100"
              onClick={() => onDelete(conversation.id)}
            >
              <Trash2 className="h-3.5 w-3.5" />
              <span className="sr-only">Delete chat</span>
            </Button>
          </div>
        ))}
      </div>
    </div>
  )
}
