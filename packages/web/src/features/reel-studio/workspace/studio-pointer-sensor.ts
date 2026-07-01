import { PointerSensor, type PointerSensorOptions } from '@dnd-kit/core'
import type { PointerEvent as ReactPointerEvent } from 'react'

import { studioPanState } from '@/features/reel-studio/workspace/studio-pan-state'

/** Ignores middle-click and space+drag so workspace panning takes priority. */
export class StudioPointerSensor extends PointerSensor {
  static activators = [
    {
      eventName: 'onPointerDown' as const,
      handler: (
        { nativeEvent: event }: ReactPointerEvent,
        _options: PointerSensorOptions,
      ) => {
        if (event.button !== 0) return false
        if (studioPanState.spacePressed || studioPanState.panning) return false
        return true
      },
    },
  ]
}
