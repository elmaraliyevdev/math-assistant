import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  gameFormSchema,
  type GameFormValues,
} from '@/features/games/schemas/game-schemas'

interface GameFormProps {
  defaultValues?: Partial<GameFormValues>
  submitLabel: string
  loading?: boolean
  onSubmit: (values: GameFormValues) => void
  onCancel?: () => void
}

export function GameForm({
  defaultValues,
  submitLabel,
  loading = false,
  onSubmit,
  onCancel,
}: GameFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<GameFormValues>({
    resolver: zodResolver(gameFormSchema),
    defaultValues: {
      name: '',
      description: '',
      ...defaultValues,
    },
  })

  return (
    <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
      <div className="space-y-2">
        <Label htmlFor="game-name">Name</Label>
        <Input id="game-name" {...register('name')} />
        {errors.name && (
          <p className="text-sm text-destructive">{errors.name.message}</p>
        )}
      </div>
      <div className="space-y-2">
        <Label htmlFor="game-description">Description</Label>
        <Textarea id="game-description" rows={4} {...register('description')} />
        {errors.description && (
          <p className="text-sm text-destructive">{errors.description.message}</p>
        )}
      </div>
      <div className="flex gap-2">
        <Button type="submit" disabled={loading}>
          {loading ? 'Saving…' : submitLabel}
        </Button>
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
        )}
      </div>
    </form>
  )
}
