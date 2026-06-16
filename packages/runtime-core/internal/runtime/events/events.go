package events

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
)

const EventVersion = "1.0.0"

type LogMode string

const (
	LogModeNone            LogMode = "none"
	LogModeTransitionsOnly LogMode = "transitions_only"
	LogModeFull            LogMode = "full"
	LogModeReplay          LogMode = "replay"
)

type Type string

const (
	TypeSpinChainStart       Type = "SPIN_CHAIN_START"
	TypeSpinChainEnd         Type = "SPIN_CHAIN_END"
	TypeFramePush            Type = "FRAME_PUSH"
	TypeFramePop             Type = "FRAME_POP"
	TypeStateEnter           Type = "STATE_ENTER"
	TypeStateReenter         Type = "STATE_REENTER"
	TypeGridResult           Type = "GRID_RESULT"
	TypeWinEvaluated         Type = "WIN_EVALUATED"
	TypeTriggerEmitted       Type = "TRIGGER_EMITTED"
	TypeTransitionTaken      Type = "TRANSITION_TAKEN"
	TypeMultiplierApplied    Type = "MULTIPLIER_APPLIED"
	TypeExposureCapApplied   Type = "EXPOSURE_CAP_APPLIED"
	TypeFeatureCounterUpdate Type = "FEATURE_COUNTER_UPDATE"
	TypeRuntimeLimitHit      Type = "RUNTIME_LIMIT_HIT"
	TypeRuntimeFault         Type = "RUNTIME_FAULT"
	TypeRNGDraw              Type = "RNG_DRAW"
	TypeGuardEvaluated       Type = "GUARD_EVALUATED"
)

type Correlation struct {
	SimulationRunID        string `json:"simulationRunId"`
	SpinChainIndex         int64  `json:"spinChainIndex"`
	GameVersionContentHash string `json:"gameVersionContentHash"`
	EngineVersion          string `json:"engineVersion"`
}

type Context struct {
	StackDepth int    `json:"stackDepth"`
	MachineID  string `json:"machineId,omitempty"`
	StateID    string `json:"stateId,omitempty"`
	FrameID    string `json:"frameId,omitempty"`
}

type Event struct {
	EventVersion string         `json:"eventVersion"`
	Sequence     int            `json:"sequence"`
	EventType    Type           `json:"eventType"`
	TimestampUs  int64          `json:"timestampUs,omitempty"`
	Correlation  Correlation    `json:"correlation"`
	Context      Context        `json:"context"`
	Payload      map[string]any `json:"payload"`
}

type replayUnit struct {
	EventVersion string         `json:"eventVersion"`
	Sequence     int            `json:"sequence"`
	EventType    Type           `json:"eventType"`
	Correlation  Correlation    `json:"correlation"`
	Context      Context        `json:"context"`
	Payload      map[string]any `json:"payload"`
}

func (e Event) ReplayUnit() replayUnit {
	return replayUnit{
		EventVersion: e.EventVersion,
		Sequence:     e.Sequence,
		EventType:    e.EventType,
		Correlation:  e.Correlation,
		Context:      e.Context,
		Payload:      e.Payload,
	}
}

type Logger struct {
	mode        LogMode
	correlation Correlation
	sequence    int
	events      []Event
}

func NewLogger(mode LogMode, correlation Correlation) *Logger {
	if mode == "" {
		mode = LogModeNone
	}
	return &Logger{mode: mode, correlation: correlation}
}

func (l *Logger) Mode() LogMode {
	return l.mode
}

func (l *Logger) Append(event Event) {
	if !ShouldEmit(event.EventType, l.mode) {
		return
	}
	event.EventVersion = EventVersion
	event.Sequence = l.sequence
	event.Correlation = l.correlation
	l.sequence++
	l.events = append(l.events, event)
}

func (l *Logger) Events() []Event {
	out := make([]Event, len(l.events))
	copy(out, l.events)
	return out
}

func (l *Logger) Hash() string {
	if len(l.events) == 0 {
		return ""
	}
	h := sha256.New()
	for _, event := range l.events {
		line, err := json.Marshal(event.ReplayUnit())
		if err != nil {
			continue
		}
		h.Write(line)
		h.Write([]byte{'\n'})
	}
	return hex.EncodeToString(h.Sum(nil))
}

func ShouldEmit(eventType Type, mode LogMode) bool {
	switch mode {
	case LogModeNone:
		return false
	case LogModeTransitionsOnly:
		return isTransitionModeEvent(eventType)
	case LogModeFull:
		return isMVPEvent(eventType)
	case LogModeReplay:
		return isMVPEvent(eventType) || eventType == TypeRNGDraw || eventType == TypeGuardEvaluated
	default:
		return false
	}
}

func isTransitionModeEvent(t Type) bool {
	switch t {
	case TypeSpinChainStart, TypeSpinChainEnd, TypeFramePush, TypeFramePop,
		TypeStateEnter, TypeTransitionTaken:
		return true
	default:
		return false
	}
}

func isMVPEvent(t Type) bool {
	switch t {
	case TypeSpinChainStart, TypeSpinChainEnd, TypeFramePush, TypeFramePop,
		TypeStateEnter, TypeStateReenter, TypeGridResult, TypeWinEvaluated,
		TypeTriggerEmitted, TypeTransitionTaken, TypeMultiplierApplied,
		TypeExposureCapApplied, TypeFeatureCounterUpdate, TypeRuntimeLimitHit,
		TypeRuntimeFault:
		return true
	default:
		return false
	}
}
