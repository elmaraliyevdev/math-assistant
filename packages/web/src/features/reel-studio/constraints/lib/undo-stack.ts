export interface UndoStackState<T> {
  past: T[]
  present: T
  future: T[]
}

export function createUndoStack<T>(initial: T): UndoStackState<T> {
  return { past: [], present: initial, future: [] }
}

export function pushUndoStack<T>(stack: UndoStackState<T>, next: T): UndoStackState<T> {
  return {
    past: [...stack.past, stack.present],
    present: next,
    future: [],
  }
}

export function undoStack<T>(stack: UndoStackState<T>): UndoStackState<T> | null {
  if (stack.past.length === 0) {
    return null
  }
  const previous = stack.past[stack.past.length - 1]!
  return {
    past: stack.past.slice(0, -1),
    present: previous,
    future: [stack.present, ...stack.future],
  }
}

export function redoStack<T>(stack: UndoStackState<T>): UndoStackState<T> | null {
  if (stack.future.length === 0) {
    return null
  }
  const [next, ...rest] = stack.future
  return {
    past: [...stack.past, stack.present],
    present: next!,
    future: rest,
  }
}
