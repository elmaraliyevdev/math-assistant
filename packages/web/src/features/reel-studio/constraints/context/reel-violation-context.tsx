import { createContext, useContext, type ReactNode } from 'react'

import { useConstraintStudio } from '@/features/reel-studio/constraints/context/constraint-studio-context'
import type {
  ConstraintValidationReport,
  ValidationResultItem,
} from '@/features/reel-studio/constraints/types'

interface ReelViolationContextValue {
  violationsByPosition: ConstraintValidationReport['violationsByPosition']
  focusedViolation: ValidationResultItem | null
}

const defaultValue: ReelViolationContextValue = {
  violationsByPosition: {},
  focusedViolation: null,
}

const ReelViolationContext = createContext<ReelViolationContextValue>(defaultValue)

export function ReelViolationBridge({ children }: { children: ReactNode }) {
  const { validation, focusedViolation } = useConstraintStudio()
  return (
    <ReelViolationContext.Provider
      value={{
        violationsByPosition: validation.violationsByPosition,
        focusedViolation,
      }}
    >
      {children}
    </ReelViolationContext.Provider>
  )
}

export function useReelViolations() {
  return useContext(ReelViolationContext)
}
