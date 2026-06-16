import { AssistantChat } from '@/features/assistant/components/AssistantChat'

export function AssistantPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Mathematics Assistant</h1>
        <p className="text-sm text-muted-foreground">
          Artifact-grounded explanations and tuning guidance for simulations and game versions.
        </p>
      </div>
      <AssistantChat />
    </div>
  )
}
