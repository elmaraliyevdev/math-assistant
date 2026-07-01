import { AssistantChat } from '@/features/assistant/components/AssistantChat'

export function AssistantPage() {
  return (
    <div className="-m-4 flex h-[calc(100dvh-3.5rem)] min-h-[32rem] flex-col overflow-hidden md:-m-6">
      <AssistantChat />
    </div>
  )
}
