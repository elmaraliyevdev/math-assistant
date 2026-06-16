package runtime

import (
	"encoding/json"

	ie "math-assistant/runtime-core/internal/runtime/events"
)

// EventType is a runtime event discriminator (Canonical Schema §12.3).
type EventType = ie.Type

const (
	EventSpinChainStart      = ie.TypeSpinChainStart
	EventSpinChainEnd        = ie.TypeSpinChainEnd
	EventFramePush           = ie.TypeFramePush
	EventFramePop            = ie.TypeFramePop
	EventStateEnter          = ie.TypeStateEnter
	EventStateReenter        = ie.TypeStateReenter
	EventGridResult          = ie.TypeGridResult
	EventWinEvaluated        = ie.TypeWinEvaluated
	EventTriggerEmitted      = ie.TypeTriggerEmitted
	EventTransitionTaken     = ie.TypeTransitionTaken
	EventMultiplierApplied   = ie.TypeMultiplierApplied
	EventExposureCapApplied  = ie.TypeExposureCapApplied
	EventFeatureCounterUpdate = ie.TypeFeatureCounterUpdate
	EventRuntimeLimitHit     = ie.TypeRuntimeLimitHit
	EventRuntimeFault        = ie.TypeRuntimeFault
	EventRNGDraw             = ie.TypeRNGDraw
	EventGuardEvaluated      = ie.TypeGuardEvaluated
)

// Event is the canonical runtime event envelope (Canonical Schema §12.2).
type Event = ie.Event

// EventCorrelation links events to a simulation run and canonical snapshot.
type EventCorrelation = ie.Correlation

// EventContext identifies the stack frame active when an event was emitted.
type EventContext = ie.Context

// NewEventLogger constructs an event logger for a spin chain.
func NewEventLogger(mode EventLogMode, correlation EventCorrelation) *EventLogger {
	return &EventLogger{inner: ie.NewLogger(ie.LogMode(mode), correlation)}
}

// EventLogger records runtime events with monotonic sequencing and replay hashing.
type EventLogger struct {
	inner *ie.Logger
}

// Mode returns the configured event log mode.
func (l *EventLogger) Mode() EventLogMode {
	return EventLogMode(l.inner.Mode())
}

// Append records an event when permitted by the active log mode.
func (l *EventLogger) Append(event Event) {
	l.inner.Append(event)
}

// Events returns emitted events in sequence order.
func (l *EventLogger) Events() []Event {
	return l.inner.Events()
}

// Hash returns SHA-256 hex over canonical JSON lines excluding timestampUs.
func (l *EventLogger) Hash() string {
	return l.inner.Hash()
}

// ShouldEmit reports whether an event type would be recorded in the given mode.
func ShouldEmit(eventType EventType, mode EventLogMode) bool {
	return ie.ShouldEmit(eventType, ie.LogMode(mode))
}

// CanonicalEventLine JSON-marshals an event for replay hashing (timestampUs omitted).
func CanonicalEventLine(event Event) ([]byte, error) {
	return json.Marshal(event.ReplayUnit())
}
