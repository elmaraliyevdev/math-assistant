import { createContext, useContext, useMemo, type ReactNode } from 'react'

export type PreviewModeValue = {
  previewMode: boolean
  readOnly: boolean
  demoMode: boolean
}

const PreviewModeContext = createContext<PreviewModeValue>({
  previewMode: false,
  readOnly: false,
  demoMode: false,
})

export function PreviewModeProvider({
  children,
  previewMode = true,
  readOnly = true,
  demoMode = true,
}: {
  children: ReactNode
  previewMode?: boolean
  readOnly?: boolean
  demoMode?: boolean
}) {
  const value = useMemo(
    () => ({ previewMode, readOnly, demoMode }),
    [demoMode, previewMode, readOnly],
  )

  return (
    <PreviewModeContext.Provider value={value}>
      {children}
    </PreviewModeContext.Provider>
  )
}

export function usePreviewMode() {
  return useContext(PreviewModeContext)
}
