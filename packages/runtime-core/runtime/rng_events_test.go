package runtime_test

import (
	"encoding/json"
	"testing"

	"math-assistant/runtime-core/runtime"
)

func TestNewRNGService(t *testing.T) {
	svc, err := runtime.NewRNGService(runtime.DefaultRNGServiceConfig())
	if err != nil {
		t.Fatal(err)
	}
	scope := svc.NewChainScope([]byte("seed"), 0, "run", 0)
	stream := scope.FrameStream("f-0-0")
	rng := stream.StepRNG(0)
	if rng.NextInt(100) < 0 {
		t.Fatal("invalid draw")
	}
}

func TestNewRNGServiceInvalid(t *testing.T) {
	_, err := runtime.NewRNGService(runtime.RNGServiceConfig{
		Algorithm: runtime.RNGAlgorithm("bad"),
		Policy:    runtime.SeedDerivationV1HashShard,
	})
	if err == nil {
		t.Fatal("expected error")
	}
}

func TestDefaultRNGServiceConfig(t *testing.T) {
	cfg := runtime.DefaultRNGServiceConfig()
	if cfg.Algorithm != runtime.RNGAlgorithmPCG64 || cfg.Policy != runtime.SeedDerivationV1HashShard {
		t.Fatalf("unexpected defaults: %+v", cfg)
	}
}

func TestMultiplierRNGPublicAPI(t *testing.T) {
	svc, _ := runtime.NewRNGService(runtime.DefaultRNGServiceConfig())
	stream := svc.NewChainScope([]byte("s"), 0, "run", 0).FrameStream("frame")
	a := stream.MultiplierRNG("m1", 0).NextUint64()
	b := stream.MultiplierRNG("m1", 1).NextUint64()
	if a == b {
		t.Fatal("multiplier streams must differ")
	}
}

func TestShouldEmitPublic(t *testing.T) {
	if runtime.ShouldEmit(runtime.EventSpinChainStart, runtime.EventLogModeNone) {
		t.Fatal("none mode should not emit")
	}
}

func TestCanonicalEventLine(t *testing.T) {
	line, err := runtime.CanonicalEventLine(runtime.Event{
		EventType:   runtime.EventSpinChainStart,
		TimestampUs: 123,
		Payload:     map[string]any{"ok": true},
	})
	if err != nil {
		t.Fatal(err)
	}
	var decoded map[string]any
	if err := json.Unmarshal(line, &decoded); err != nil {
		t.Fatal(err)
	}
	if _, ok := decoded["timestampUs"]; ok {
		t.Fatal("canonical line must not include timestamp from ReplayUnit path")
	}
}

func TestEventLoggerAppendAndHash(t *testing.T) {
	logger := runtime.NewEventLogger(runtime.EventLogModeFull, runtime.EventCorrelation{
		SimulationRunID:        "run",
		SpinChainIndex:         0,
		GameVersionContentHash: "hash",
		EngineVersion:          runtime.EngineVersion,
	})
	logger.Append(runtime.Event{EventType: runtime.EventSpinChainStart})
	if len(logger.Events()) != 1 {
		t.Fatal("expected one event")
	}
	if logger.Hash() == "" {
		t.Fatal("expected non-empty hash")
	}
}
