import { CircleHelp } from 'lucide-react'
import { Label } from '@/components/ui/label'

interface FieldHelpProps {
  description: string
}

export function FieldHelp({ description }: FieldHelpProps) {
  return (
    <button
      type="button"
      className="inline-flex text-muted-foreground hover:text-foreground"
      title={description}
      aria-label="Show help"
    >
      <CircleHelp className="h-3.5 w-3.5" />
    </button>
  )
}

interface FieldLabelProps {
  htmlFor: string
  label: string
  description?: string
}

export function FieldLabel({ htmlFor, label, description }: FieldLabelProps) {
  return (
    <div className="flex items-center gap-1">
      <Label htmlFor={htmlFor}>{label}</Label>
      {description ? <FieldHelp description={description} /> : null}
    </div>
  )
}
