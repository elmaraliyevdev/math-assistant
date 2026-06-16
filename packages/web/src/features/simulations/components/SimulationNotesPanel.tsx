import { Trash2 } from 'lucide-react'
import { useState } from 'react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import {
  useCreateSimulationNote,
  useDeleteSimulationNote,
  useSimulationNotes,
} from '@/features/simulations/hooks/use-simulations'
import { formatDate } from '@/lib/utils'

interface SimulationNotesPanelProps {
  simulationId: string
  enabled?: boolean
}

export function SimulationNotesPanel({
  simulationId,
  enabled = true,
}: SimulationNotesPanelProps) {
  const notes = useSimulationNotes(simulationId, enabled)
  const createNote = useCreateSimulationNote(simulationId)
  const deleteNote = useDeleteSimulationNote(simulationId)
  const [draft, setDraft] = useState('')

  return (
    <Card>
      <CardHeader>
        <CardTitle>Simulation notes</CardTitle>
        <p className="text-sm text-muted-foreground">
          Document tuning decisions for this run.
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Textarea
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder='Example: "Reduced scatter frequency from 68% to 35%."'
            rows={3}
          />
          <Button
            onClick={() => {
              const content = draft.trim()
              if (!content) return
              createNote.mutate(content, {
                onSuccess: () => setDraft(''),
              })
            }}
            disabled={createNote.isPending || draft.trim().length === 0}
          >
            Add note
          </Button>
        </div>

        {notes.isLoading && (
          <p className="text-sm text-muted-foreground">Loading notes…</p>
        )}

        {notes.data?.items.length === 0 && !notes.isLoading && (
          <p className="text-sm text-muted-foreground">No notes yet.</p>
        )}

        <ul className="space-y-3">
          {notes.data?.items.map((note) => (
            <li key={note.id} className="rounded-lg border p-3">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-sm">{note.content}</p>
                  <p className="mt-2 text-xs text-muted-foreground">
                    {formatDate(note.createdAt)}
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label="Delete note"
                  onClick={() => deleteNote.mutate(note.id)}
                  disabled={deleteNote.isPending}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}
