package session

import (
	"testing"

	"math-assistant/runtime-core/internal/domain"
)

func testGame() *domain.GameVersion {
	return &domain.GameVersion{
		SchemaVersion: "1.0.0",
		ContentHash:   "fixed-content-hash",
		BetModel: domain.BetModel{
			Type:             "lines",
			LineCount:        20,
			CoinValueScale:   100,
			DefaultCoinValue: 2,
		},
		Session: domain.SessionConfig{
			MaxStackDepth:            6,
			ContextInheritancePolicy: "mvp-v1",
			RuntimeLimits: &domain.RuntimeLimits{
				MaxStepsPerSpinChain: 100,
				MaxEventsPerChain:    500,
			},
		},
		Exposure: domain.Exposure{
			MaxWinMinorUnits: 10000,
			MaxWinMultiplier: 100,
			CapScope:         "session_spin_chain",
			EnforceCap:       true,
		},
		Determinism: domain.Determinism{
			RngAlgorithm:         "PCG64",
			SeedDerivationPolicy: "v1-hash-shard",
			MoneyRepresentation:  "fixed_minor_units",
		},
	}
}

func validParams() Params {
	return Params{
		Game:            testGame(),
		EngineVersion:   "runtime-core@1.0.0",
		MasterSeed:      []byte("seed"),
		SpinChainIndex:  1,
		ShardIndex:      0,
		SimulationRunID: "sim-run",
	}
}

func TestNewSessionSuccess(t *testing.T) {
	s, err := New(validParams())
	if err != nil {
		t.Fatal(err)
	}
	if s.GameVersionContentHash != "fixed-content-hash" {
		t.Fatalf("content hash = %q", s.GameVersionContentHash)
	}
	if s.TotalBetMinorUnits != 4000 {
		t.Fatalf("total bet = %d, want 20*2*100", s.TotalBetMinorUnits)
	}
	if s.InheritancePolicy != "mvp-v1" {
		t.Fatalf("inheritance = %q", s.InheritancePolicy)
	}
	if s.Limits.MaxStepsPerSpinChain != 100 {
		t.Fatalf("limits steps = %d", s.Limits.MaxStepsPerSpinChain)
	}
	if s.Limits.MaxFramesPerChain != 6 {
		t.Fatalf("max frames capped by stack depth = %d", s.Limits.MaxFramesPerChain)
	}
	if s.Exposure.EffectiveCapMinor != 10000 {
		t.Fatalf("effective cap = %d, want min(10000, 100*4000)", s.Exposure.EffectiveCapMinor)
	}
}

func TestNewSessionRequiredFields(t *testing.T) {
	p := validParams()
	p.Game = nil
	if _, err := New(p); err == nil {
		t.Fatal("expected error for nil game")
	}
	p = validParams()
	p.EngineVersion = ""
	if _, err := New(p); err == nil {
		t.Fatal("expected error for empty engine version")
	}
	p = validParams()
	p.MasterSeed = nil
	if _, err := New(p); err == nil {
		t.Fatal("expected error for empty master seed")
	}
	p = validParams()
	p.SimulationRunID = ""
	if _, err := New(p); err == nil {
		t.Fatal("expected error for empty simulation run id")
	}
}

func TestResolveBetOverride(t *testing.T) {
	p := validParams()
	p.BetMinorUnits = 777
	s, err := New(p)
	if err != nil {
		t.Fatal(err)
	}
	if s.TotalBetMinorUnits != 777 || s.Bet.TotalBetMinorUnits != 777 {
		t.Fatalf("bet override not applied: %+v", s.Bet)
	}
}

func TestResolveBetTotalBetMinorUnitsField(t *testing.T) {
	game := testGame()
	game.BetModel.TotalBetMinorUnits = 2500
	s, err := New(Params{Game: game, EngineVersion: "e", MasterSeed: []byte("s"), SimulationRunID: "r"})
	if err != nil {
		t.Fatal(err)
	}
	if s.TotalBetMinorUnits != 2500 {
		t.Fatalf("total bet = %d", s.TotalBetMinorUnits)
	}
}

func TestResolveBetDefaultsLinesToOne(t *testing.T) {
	game := testGame()
	game.BetModel.LineCount = 0
	game.BetModel.CoinValueScale = 0
	game.BetModel.DefaultCoinValue = 0
	s, err := New(Params{Game: game, EngineVersion: "e", MasterSeed: []byte("s"), SimulationRunID: "r"})
	if err != nil {
		t.Fatal(err)
	}
	if s.TotalBetMinorUnits != 1 {
		t.Fatalf("total bet = %d, want 1", s.TotalBetMinorUnits)
	}
}

func TestValidateDeterminism(t *testing.T) {
	game := testGame()
	game.Determinism.RngAlgorithm = "MT19937"
	if _, err := New(Params{Game: game, EngineVersion: "e", MasterSeed: []byte("s"), SimulationRunID: "r"}); err == nil {
		t.Fatal("expected determinism error")
	}
	game = testGame()
	game.Determinism.SeedDerivationPolicy = "legacy"
	if _, err := New(Params{Game: game, EngineVersion: "e", MasterSeed: []byte("s"), SimulationRunID: "r"}); err == nil {
		t.Fatal("expected seed policy error")
	}
	game = testGame()
	game.Determinism.MoneyRepresentation = "float"
	if _, err := New(Params{Game: game, EngineVersion: "e", MasterSeed: []byte("s"), SimulationRunID: "r"}); err == nil {
		t.Fatal("expected money representation error")
	}
}

func TestContentHashComputedWhenMissing(t *testing.T) {
	game := testGame()
	game.ContentHash = ""
	s, err := New(Params{Game: game, EngineVersion: "e", MasterSeed: []byte("s"), SimulationRunID: "r"})
	if err != nil {
		t.Fatal(err)
	}
	if len(s.GameVersionContentHash) != 64 {
		t.Fatalf("expected sha256 hex hash, got %q", s.GameVersionContentHash)
	}
}

func TestPlatformLimitsDefaults(t *testing.T) {
	game := testGame()
	game.Session.RuntimeLimits = nil
	game.Session.MaxStackDepth = 0
	s, err := New(Params{Game: game, EngineVersion: "e", MasterSeed: []byte("s"), SimulationRunID: "r"})
	if err != nil {
		t.Fatal(err)
	}
	if s.Limits.MaxStepsPerSpinChain != 500 {
		t.Fatalf("default steps = %d", s.Limits.MaxStepsPerSpinChain)
	}
	if s.Limits.MaxFramesPerChain != 8 {
		t.Fatalf("default frames = %d", s.Limits.MaxFramesPerChain)
	}
}

func TestExposureCapUsesMultiplierWhenSmaller(t *testing.T) {
	game := testGame()
	s, err := New(Params{Game: game, EngineVersion: "e", MasterSeed: []byte("s"), SimulationRunID: "r"})
	if err != nil {
		t.Fatal(err)
	}
	// totalBet = 4000, multiplier cap = 100 * 4000 = 400000, maxWin = 10000
	if s.Exposure.EffectiveCapMinor != 10000 {
		t.Fatalf("cap = %d", s.Exposure.EffectiveCapMinor)
	}
	game.Exposure.MaxWinMinorUnits = 500000
	s, err = New(Params{Game: game, EngineVersion: "e", MasterSeed: []byte("s"), SimulationRunID: "r"})
	if err != nil {
		t.Fatal(err)
	}
	if s.Exposure.EffectiveCapMinor != 400000 {
		t.Fatalf("cap = %d, want multiplier-bound cap", s.Exposure.EffectiveCapMinor)
	}
}

func TestExposureCapUsesMaxWinMinorUnitsWhenSmaller(t *testing.T) {
	game := testGame()
	game.Exposure.MaxWinMultiplier = 0
	game.Exposure.MaxWinMinorUnits = 500
	s, err := New(Params{Game: game, EngineVersion: "e", MasterSeed: []byte("s"), SimulationRunID: "r"})
	if err != nil {
		t.Fatal(err)
	}
	if s.Exposure.EffectiveCapMinor != 500 {
		t.Fatalf("cap = %d", s.Exposure.EffectiveCapMinor)
	}
}

func TestResolveLimitsOverridesAllFields(t *testing.T) {
	game := testGame()
	game.Session.RuntimeLimits = &domain.RuntimeLimits{
		MaxStepsPerSpinChain:   1,
		MaxFramesPerChain:      2,
		MaxTransitionsPerStep:  3,
		MaxRespinsPerFeature:   4,
		MaxEventsPerChain:      5,
		MaxWallClockMsPerChain: 6,
	}
	game.Session.MaxStackDepth = 10
	s, err := New(Params{Game: game, EngineVersion: "e", MasterSeed: []byte("s"), SimulationRunID: "r"})
	if err != nil {
		t.Fatal(err)
	}
	l := s.Limits
	if l.MaxStepsPerSpinChain != 1 || l.MaxFramesPerChain != 2 || l.MaxTransitionsPerStep != 3 ||
		l.MaxRespinsPerFeature != 4 || l.MaxEventsPerChain != 5 || l.MaxWallClockMsPerChain != 6 {
		t.Fatalf("limits not fully overridden: %+v", l)
	}
}

func TestDefaultInheritancePolicy(t *testing.T) {
	game := testGame()
	game.Session.ContextInheritancePolicy = ""
	s, err := New(Params{Game: game, EngineVersion: "e", MasterSeed: []byte("s"), SimulationRunID: "r"})
	if err != nil {
		t.Fatal(err)
	}
	if s.InheritancePolicy != "mvp-v1" {
		t.Fatalf("policy = %q", s.InheritancePolicy)
	}
}
