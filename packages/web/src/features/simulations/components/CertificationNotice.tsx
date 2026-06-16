interface CertificationNoticeProps {
  notice?: string
}

export function CertificationNotice({ notice }: CertificationNoticeProps) {
  if (!notice) {
    return null
  }

  return (
    <div className="rounded-lg border border-primary/20 bg-primary/5 px-4 py-3 text-sm text-foreground">
      {notice}
    </div>
  )
}
