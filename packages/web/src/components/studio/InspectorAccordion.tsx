import { createContext, useContext, useMemo, useState, type ReactNode } from 'react'

type InspectorAccordionContextValue = {
  openId: string | null
  toggle: (id: string) => void
}

const InspectorAccordionContext = createContext<InspectorAccordionContextValue | null>(null)

export function InspectorAccordion({
  children,
  defaultOpenId = null,
}: {
  children: ReactNode
  defaultOpenId?: string | null
}) {
  const [openId, setOpenId] = useState<string | null>(defaultOpenId)

  const value = useMemo(
    () => ({
      openId,
      toggle: (id: string) => setOpenId((current) => (current === id ? null : id)),
    }),
    [openId],
  )

  return (
    <InspectorAccordionContext.Provider value={value}>
      {children}
    </InspectorAccordionContext.Provider>
  )
}

export function useInspectorAccordion() {
  return useContext(InspectorAccordionContext)
}
