import { Link } from '@tanstack/react-router'

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { CitationPanel } from '@/features/assistant/components/CitationPanel'
import type { AssistantChatMessage } from '@/features/assistant/types'
import { cn } from '@/lib/utils'

export function AssistantRichResponse({
  message,
  simulationId,
  gameVersionId,
  gameId,
  onFollowUp,
}: {
  message: AssistantChatMessage
  simulationId?: string
  gameVersionId?: string
  gameId?: string
  onFollowUp?: (prompt: string) => void
}) {
  const sections =
    message.sections && message.sections.length > 0
      ? message.sections
      : message.content
        ? [{ title: 'Summary', content: message.content }]
        : []

  return (
    <div className="space-y-3">
      {message.isStreaming && !message.content ? (
        <TypingIndicator />
      ) : null}

      <Accordion
        type="multiple"
        defaultValue={sections.slice(0, 2).map((_, index) => `section-${index}`)}
        className="space-y-2"
      >
        {sections.map((section, index) => (
          <AccordionItem
            key={`${section.title}-${index}`}
            value={`section-${index}`}
            className="rounded-xl border border-border/40 px-3"
          >
            <AccordionTrigger className="py-3 text-sm font-medium hover:no-underline">
              {section.title}
            </AccordionTrigger>
            <AccordionContent className="pb-3 text-sm text-muted-foreground whitespace-pre-wrap">
              {section.content}
            </AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>

      {message.recommendations && message.recommendations.length > 0 ? (
        <div className="space-y-2">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Recommendations
          </p>
          {message.recommendations.map((item, index) => (
            <div
              key={`${item.action}-${index}`}
              className="rounded-xl border border-border/40 bg-card/40 p-3"
            >
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant="secondary" className="capitalize">
                  {item.severity}
                </Badge>
                <span className="text-sm font-medium">{item.action}</span>
              </div>
              <p className="mt-2 text-sm text-muted-foreground">{item.category}</p>
              <p className="mt-2 text-xs text-muted-foreground">
                Expected impact {item.expectedRtpImpact}
                {item.estimatedRtpContributionPp
                  ? ` · ${item.estimatedRtpContributionPp.toFixed(2)} pp`
                  : ''}
              </p>
            </div>
          ))}
        </div>
      ) : null}

      {message.citations && message.citations.length > 0 ? (
        <CitationPanel citations={message.citations} />
      ) : null}

      <div className="flex flex-wrap gap-2">
        {simulationId ? (
          <Button size="sm" variant="outline" asChild>
            <Link to="/simulations/$simulationId" params={{ simulationId }}>
              View simulation
            </Link>
          </Button>
        ) : null}
        {gameVersionId && gameId ? (
          <Button size="sm" variant="outline" asChild>
            <Link
              to="/games/$gameId/versions/$versionId/reel-studio"
              params={{ gameId, versionId: gameVersionId }}
            >
              Open Studio
            </Link>
          </Button>
        ) : null}
      </div>

      {message.followUps && message.followUps.length > 0 && onFollowUp ? (
        <div className="flex flex-wrap gap-2 pt-1">
          {message.followUps.map((prompt) => (
            <button
              key={prompt}
              type="button"
              onClick={() => onFollowUp(prompt)}
              className={cn(
                'rounded-full border border-border/40 px-3 py-1.5 text-xs',
                'transition-colors hover:border-primary/30 hover:bg-primary/5',
              )}
            >
              {prompt}
            </button>
          ))}
        </div>
      ) : null}
    </div>
  )
}

function TypingIndicator() {
  return (
    <div className="flex items-center gap-2 text-sm text-muted-foreground">
      <span className="inline-flex gap-1">
        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-primary [animation-delay:0ms]" />
        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-primary [animation-delay:120ms]" />
        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-primary [animation-delay:240ms]" />
      </span>
      Generating analysis…
    </div>
  )
}

export function AssistantUserBubble({ content }: { content: string }) {
  return (
    <div className="flex justify-end">
      <div className="max-w-[85%] rounded-2xl rounded-br-md bg-primary px-4 py-2.5 text-sm text-primary-foreground">
        <p className="whitespace-pre-wrap">{content}</p>
      </div>
    </div>
  )
}

export function AssistantAssistantBubble({
  message,
  simulationId,
  gameVersionId,
  gameId,
  onFollowUp,
}: {
  message: AssistantChatMessage
  simulationId?: string
  gameVersionId?: string
  gameId?: string
  onFollowUp?: (prompt: string) => void
}) {
  return (
    <div className="flex justify-start">
      <div className="max-w-[92%] rounded-2xl rounded-bl-md border border-border/40 bg-card/60 px-4 py-3">
        <AssistantRichResponse
          message={message}
          simulationId={simulationId}
          gameVersionId={gameVersionId}
          gameId={gameId}
          onFollowUp={onFollowUp}
        />
      </div>
    </div>
  )
}
