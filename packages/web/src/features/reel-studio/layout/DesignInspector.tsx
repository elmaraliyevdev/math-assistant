import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion'
import { CandidateComparisonContent } from '@/features/reel-studio/generator/components/CandidateComparisonPanel'
import { DesignGoalsContent } from '@/features/reel-studio/generator/components/DesignGoalsPanel'
import { DesignHealthContent } from '@/features/reel-studio/generator/components/DesignHealthPanel'
import { SmartSuggestionsContent } from '@/features/reel-studio/generator/components/SmartSuggestionsPanel'
import { useGeneratorStudio } from '@/features/reel-studio/generator/context/generator-context'

export function DesignInspector() {
  const { designHealth, designGoals, report, suggestions } = useGeneratorStudio()
  const visibleSuggestions = suggestions.length
  const defaultSections = ['health', 'goals']
  if (report) defaultSections.push('candidates')
  if (visibleSuggestions > 0) defaultSections.push('suggestions')

  return (
    <Accordion
      type="multiple"
      defaultValue={defaultSections}
      className="w-full"
    >
      <AccordionItem value="health">
        <AccordionTrigger>
          <span>Design health</span>
          <span className="ml-auto mr-2 text-xs font-semibold tabular-nums text-primary">
            {designHealth.overallScore}
          </span>
        </AccordionTrigger>
        <AccordionContent>
          <DesignHealthContent />
        </AccordionContent>
      </AccordionItem>

      <AccordionItem value="goals">
        <AccordionTrigger>
          <span>Goals</span>
          <span className="ml-auto mr-2 text-xs text-muted-foreground">
            {designGoals.targetRtpPercent}% RTP
          </span>
        </AccordionTrigger>
        <AccordionContent>
          <DesignGoalsContent />
        </AccordionContent>
      </AccordionItem>

      {visibleSuggestions > 0 ? (
        <AccordionItem value="suggestions">
          <AccordionTrigger>
            <span>Suggestions</span>
            <span className="ml-auto mr-2 text-xs text-muted-foreground">{visibleSuggestions}</span>
          </AccordionTrigger>
          <AccordionContent>
            <SmartSuggestionsContent />
          </AccordionContent>
        </AccordionItem>
      ) : null}

      {report ? (
        <AccordionItem value="candidates">
          <AccordionTrigger>
            <span>Candidates</span>
            <span className="ml-auto mr-2 text-xs text-muted-foreground">
              {report.candidates.length}
            </span>
          </AccordionTrigger>
          <AccordionContent>
            <CandidateComparisonContent />
          </AccordionContent>
        </AccordionItem>
      ) : null}
    </Accordion>
  )
}
