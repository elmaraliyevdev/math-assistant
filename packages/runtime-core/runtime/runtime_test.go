package runtime_test

import (
	"testing"

	"math-assistant/runtime-core/internal/domain"
	"math-assistant/runtime-core/runtime"
)

func testGame() *domain.GameVersion {
	return &domain.GameVersion{
		ContentHash: "hash-001",
		BetModel: domain.BetModel{
			Type:               "lines",
			LineCount:          10,
			CoinValueScale:     1,
			DefaultCoinValue:   1,
			TotalBetMinorUnits: 100,
		},
		Session: domain.SessionConfig{MaxStackDepth: 4},
		Exposure: domain.Exposure{
			MaxWinMinorUnits: 1000,
			EnforceCap:       true,
			CapScope:         "session_spin_chain",
		},
		Determinism: domain.Determinism{RngAlgorithm: "PCG64"},
	}
}

func TestNewSessionContextError(t *testing.T) {
	_, err := runtime.NewSessionContext(runtime.NewSessionParams{
		Game: testGame(),
	})
	if err == nil {
		t.Fatal("expected error for missing required params")
	}
}

func TestNewSessionContextRNGError(t *testing.T) {
	_, err := runtime.NewSessionContext(runtime.NewSessionParams{
		Game:            testGame(),
		EngineVersion:   runtime.EngineVersion,
		MasterSeed:      []byte("master"),
		SimulationRunID: "sim-1",
		RNGConfig: runtime.RNGServiceConfig{
			Algorithm: runtime.RNGAlgorithmPCG64,
			Policy:    runtime.SeedDerivationPolicy("bad"),
		},
	})
	if err == nil {
		t.Fatal("expected rng service error")
	}
}

func TestNewSessionContext(t *testing.T) {
	ctx, err := runtime.NewSessionContext(runtime.NewSessionParams{
		Game:            testGame(),
		EngineVersion:   runtime.EngineVersion,
		MasterSeed:      []byte("master"),
		SpinChainIndex:  3,
		ShardIndex:      1,
		SimulationRunID: "sim-1",
		EventLogMode:    runtime.EventLogModeFull,
		RNGConfig:       runtime.DefaultRNGServiceConfig(),
	})
	if err != nil {
		t.Fatal(err)
	}
	if ctx.RNG == nil || ctx.ChainRNG.ChainSeed() == nil || ctx.Events == nil {
		t.Fatal("expected rng, chain scope, and event logger")
	}
	if ctx.TotalBetMinorUnits != 100 {
		t.Fatalf("bet = %d", ctx.TotalBetMinorUnits)
	}
	if ctx.Events.Mode() != runtime.EventLogModeFull {
		t.Fatalf("event mode = %q", ctx.Events.Mode())
	}
}

func TestNewSessionParamsFromRequest(t *testing.T) {
	req := runtime.SpinChainRequest{
		Game:            testGame(),
		MasterSeed:      []byte("m"),
		SpinChainIndex:  2,
		BetMinorUnits:   555,
		SimulationRunID: "run",
		EventLogMode:    runtime.EventLogModeTransitionsOnly,
	}
	params := runtime.NewSessionParamsFromRequest(req)
	if params.EngineVersion != runtime.EngineVersion {
		t.Fatalf("engine version = %q", params.EngineVersion)
	}
	ctx, err := runtime.NewSessionContext(params)
	if err != nil {
		t.Fatal(err)
	}
	if ctx.TotalBetMinorUnits != 555 {
		t.Fatalf("bet override = %d", ctx.TotalBetMinorUnits)
	}
}

func TestFrameContext(t *testing.T) {
	fc := runtime.NewFrameContext()
	if fc.FrameLocalState == nil {
		t.Fatal("FrameLocalState map must be initialized")
	}
	fc.SpinsRemaining = 10
	fc.HeldSymbols = append(fc.HeldSymbols, runtime.HeldSymbol{Reel: 1, Row: 2, SymbolID: "BONUS"})
	if fc.SpinsRemaining != 10 || len(fc.HeldSymbols) != 1 {
		t.Fatal("frame context fields not set")
	}
}

func TestSpinChainTypesCompile(t *testing.T) {
	result := runtime.SpinChainResult{
		TotalWinMinorUnits: 10,
		AccumulatorDelta: runtime.AccumulatorDelta{
			CappedWinMinorUnits: 10,
		},
		LimitHit: &runtime.LimitHit{Code: "MAX_STEPS", Action: "fail_chain"},
	}
	if result.LimitHit.Code != "MAX_STEPS" {
		t.Fatal("unexpected limit hit")
	}
}
