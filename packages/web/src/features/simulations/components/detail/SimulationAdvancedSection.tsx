import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion'
import { SimulationIntelligencePanel } from '@/features/simulation-intelligence/components/SimulationIntelligencePanel'
import { DistributedSimulationPanel } from '@/features/distributed/components/DistributedSimulationPanel'
import { CalibrationDashboard } from '@/features/workbench/components/CalibrationDashboard'
import {
  CertificationNotice,
  MathConfigurationSnapshot,
  SimulationNotesPanel,
} from '@/features/simulations/components'
import type { CalibrateResponse, SimulationDetail, SimulationResults } from '@/types/api'

export function SimulationAdvancedSection({
  detail,
  results,
  calibration,
  calibrationLoading,
  calibrationError,
  canonicalJson,
}: {
  detail: SimulationDetail
  results: SimulationResults
  calibration?: CalibrateResponse
  calibrationLoading?: boolean
  calibrationError?: string | null
  canonicalJson?: Record<string, unknown>
}) {
  return (
    <section>
      <Accordion type="single" collapsible className="rounded-xl border border-border/40 px-4">
        <AccordionItem value="advanced" className="border-0">
          <AccordionTrigger className="py-4 text-base font-medium hover:no-underline">
            Advanced analysis
          </AccordionTrigger>
          <AccordionContent className="space-y-6 pb-6">
            <CertificationNotice notice={results.certificationNotice} />
            {results.simulationIntelligence ? (
              <SimulationIntelligencePanel intelligence={results.simulationIntelligence} />
            ) : null}
            <CalibrationDashboard
              data={calibration}
              isLoading={calibrationLoading}
              error={calibrationError}
            />
            <DistributedSimulationPanel
              simulationId={detail.id}
              distributedExecution={Boolean(detail.distributedExecution)}
              enabled={detail.status === 'running' || detail.status === 'completed'}
            />
            {canonicalJson ? (
              <MathConfigurationSnapshot canonicalJson={canonicalJson} />
            ) : null}
            <SimulationNotesPanel simulationId={detail.id} />
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </section>
  )
}
