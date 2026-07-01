let spacePressed = false
let panning = false

export const studioPanState = {
  get spacePressed() {
    return spacePressed
  },
  set spacePressed(value: boolean) {
    spacePressed = value
  },
  get panning() {
    return panning
  },
  set panning(value: boolean) {
    panning = value
  },
}
