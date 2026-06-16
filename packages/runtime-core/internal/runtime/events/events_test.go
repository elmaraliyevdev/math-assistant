package events

import (
	"testing"
)

func correlation() Correlation {
	return Correlation{
		SimulationRunID:        "run-1",
		SpinChainIndex:         7,
		GameVersionContentHash: "abc123",
		EngineVersion:          "runtime-core@1.0.0",
	}
}

func TestShouldEmitModes(t *testing.T) {
	cases := []struct {
		mode   LogMode
		typ    Type
		want   bool
	}{
		{LogModeNone, TypeSpinChainStart, false},
		{LogModeTransitionsOnly, TypeSpinChainStart, true},
		{LogModeTransitionsOnly, TypeWinEvaluated, false},
		{LogModeFull, TypeWinEvaluated, true},
		{LogModeFull, TypeRNGDraw, false},
		{LogModeReplay, TypeRNGDraw, true},
		{LogModeReplay, TypeGuardEvaluated, true},
		{"unknown", TypeSpinChainStart, false},
	}
	for _, tc := range cases {
		if got := ShouldEmit(tc.typ, tc.mode); got != tc.want {
			t.Fatalf("ShouldEmit(%q, %q) = %v, want %v", tc.typ, tc.mode, got, tc.want)
		}
	}
}

func TestLoggerAppendSequenceAndCorrelation(t *testing.T) {
	logger := NewLogger(LogModeFull, correlation())
	logger.Append(Event{EventType: TypeSpinChainStart, Payload: map[string]any{"k": "v"}})
	logger.Append(Event{EventType: TypeSpinChainEnd})
	events := logger.Events()
	if len(events) != 2 {
		t.Fatalf("len(events) = %d", len(events))
	}
	if events[0].Sequence != 0 || events[1].Sequence != 1 {
		t.Fatalf("sequences = %d,%d", events[0].Sequence, events[1].Sequence)
	}
	if events[0].EventVersion != EventVersion {
		t.Fatalf("eventVersion = %q", events[0].EventVersion)
	}
	if events[0].Correlation.SimulationRunID != "run-1" {
		t.Fatalf("correlation not applied: %+v", events[0].Correlation)
	}
}

func TestLoggerFiltersByMode(t *testing.T) {
	logger := NewLogger(LogModeTransitionsOnly, correlation())
	logger.Append(Event{EventType: TypeWinEvaluated})
	logger.Append(Event{EventType: TypeTransitionTaken})
	if len(logger.Events()) != 1 {
		t.Fatalf("expected 1 event, got %d", len(logger.Events()))
	}
}

func TestLoggerDefaultModeNone(t *testing.T) {
	logger := NewLogger("", correlation())
	logger.Append(Event{EventType: TypeSpinChainStart})
	if len(logger.Events()) != 0 {
		t.Fatal("empty mode should default to none")
	}
}

func TestLoggerHashStableWithoutTimestamp(t *testing.T) {
	logger := NewLogger(LogModeFull, correlation())
	logger.Append(Event{
		EventType:   TypeSpinChainStart,
		TimestampUs: 111,
		Payload:     map[string]any{"a": 1},
	})
	hashA := logger.Hash()

	logger2 := NewLogger(LogModeFull, correlation())
	logger2.Append(Event{
		EventType:   TypeSpinChainStart,
		TimestampUs: 999,
		Payload:     map[string]any{"a": 1},
	})
	hashB := logger2.Hash()
	if hashA != hashB {
		t.Fatalf("hash must exclude timestampUs: %q vs %q", hashA, hashB)
	}
}

func TestLoggerHashEmpty(t *testing.T) {
	logger := NewLogger(LogModeFull, correlation())
	if logger.Hash() != "" {
		t.Fatal("empty logger hash must be empty string")
	}
}

func TestReplayUnitOmitsTimestamp(t *testing.T) {
	event := Event{
		EventVersion: EventVersion,
		Sequence:     3,
		EventType:    TypeGridResult,
		TimestampUs:  42,
		Payload:      map[string]any{"x": true},
	}
	unit := event.ReplayUnit()
	if unit.Sequence != 3 || unit.EventType != TypeGridResult {
		t.Fatalf("unexpected replay unit: %+v", unit)
	}
}

func TestIsTransitionModeEventCoverage(t *testing.T) {
	if !isTransitionModeEvent(TypeFramePop) {
		t.Fatal("FRAME_POP should be transition mode event")
	}
	if isTransitionModeEvent(TypeRuntimeFault) {
		t.Fatal("RUNTIME_FAULT should not be transition mode event")
	}
}

func TestIsMVPEventCoverage(t *testing.T) {
	if !isMVPEvent(TypeFeatureCounterUpdate) {
		t.Fatal("FEATURE_COUNTER_UPDATE should be MVP event")
	}
	if isMVPEvent(TypeRNGDraw) {
		t.Fatal("RNG_DRAW is replay-only, not MVP full set")
	}
}

func TestLoggerEventsReturnsCopy(t *testing.T) {
	logger := NewLogger(LogModeFull, correlation())
	logger.Append(Event{EventType: TypeSpinChainStart})
	events := logger.Events()
	events[0].Sequence = 99
	if logger.Events()[0].Sequence == 99 {
		t.Fatal("Events() must return a defensive copy")
	}
}

func TestLoggerMode(t *testing.T) {
	logger := NewLogger(LogModeReplay, correlation())
	if logger.Mode() != LogModeReplay {
		t.Fatalf("Mode() = %q", logger.Mode())
	}
}
