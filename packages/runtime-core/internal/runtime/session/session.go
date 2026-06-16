package session

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"

	"math-assistant/runtime-core/internal/domain"
)

type EventLogMode string

type RNGAlgorithm string

type RNGPolicy string

type RNGConfig struct {
	Algorithm RNGAlgorithm
	Policy    RNGPolicy
}

type Params struct {
	Game            *domain.GameVersion
	EngineVersion   string
	MasterSeed      []byte
	SpinChainIndex  int64
	ShardIndex      int
	SimulationRunID string
	BetMinorUnits   int64
	EventLogMode    EventLogMode
	RNGConfig       RNGConfig
}

type BetContext struct {
	LineCount          int
	CoinValueScale     int
	DefaultCoinValue   int
	TotalBetMinorUnits int64
	BetModelType       string
}

type EffectiveLimits struct {
	MaxStepsPerSpinChain   int
	MaxFramesPerChain      int
	MaxTransitionsPerStep  int
	MaxRespinsPerFeature   int
	MaxEventsPerChain      int
	MaxWallClockMsPerChain int
}

type ExposureState struct {
	EnforceCap        bool
	EffectiveCapMinor int64
	CapScope          string
	MaxWinMinorUnits  int64
	MaxWinMultiplier  int64
}

type Session struct {
	GameVersionContentHash string
	EngineVersion          string
	SpinChainIndex         int64
	Bet                    BetContext
	TotalBetMinorUnits     int64
	InheritancePolicy      string
	Limits                 EffectiveLimits
	Exposure               ExposureState
}

func New(params Params) (*Session, error) {
	if params.Game == nil {
		return nil, fmt.Errorf("game is required")
	}
	if params.EngineVersion == "" {
		return nil, fmt.Errorf("engineVersion is required")
	}
	if len(params.MasterSeed) == 0 {
		return nil, fmt.Errorf("masterSeed is required")
	}
	if params.SimulationRunID == "" {
		return nil, fmt.Errorf("simulationRunID is required")
	}
	if err := validateDeterminism(params.Game); err != nil {
		return nil, err
	}
	hash, err := contentHash(params.Game)
	if err != nil {
		return nil, err
	}
	bet, totalBet, err := resolveBet(params.Game, params.BetMinorUnits)
	if err != nil {
		return nil, err
	}
	limits := resolveLimits(params.Game)
	exposure := resolveExposure(params.Game, totalBet)
	policy := params.Game.Session.ContextInheritancePolicy
	if policy == "" {
		policy = "mvp-v1"
	}
	return &Session{
		GameVersionContentHash: hash,
		EngineVersion:          params.EngineVersion,
		SpinChainIndex:         params.SpinChainIndex,
		Bet:                    bet,
		TotalBetMinorUnits:     totalBet,
		InheritancePolicy:      policy,
		Limits:                 limits,
		Exposure:               exposure,
	}, nil
}

func validateDeterminism(game *domain.GameVersion) error {
	d := game.Determinism
	if d.RngAlgorithm != "PCG64" {
		return fmt.Errorf("unsupported determinism.rngAlgorithm %q (MVP requires PCG64)", d.RngAlgorithm)
	}
	if d.SeedDerivationPolicy != "" && d.SeedDerivationPolicy != "v1-hash-shard" {
		return fmt.Errorf("unsupported determinism.seedDerivationPolicy %q", d.SeedDerivationPolicy)
	}
	if d.MoneyRepresentation != "" && d.MoneyRepresentation != "fixed_minor_units" {
		return fmt.Errorf("unsupported determinism.moneyRepresentation %q", d.MoneyRepresentation)
	}
	return nil
}

func contentHash(game *domain.GameVersion) (string, error) {
	if game.ContentHash != "" {
		return game.ContentHash, nil
	}
	raw, err := json.Marshal(game)
	if err != nil {
		return "", fmt.Errorf("marshal game for content hash: %w", err)
	}
	sum := sha256.Sum256(raw)
	return hex.EncodeToString(sum[:]), nil
}

func resolveBet(game *domain.GameVersion, override int64) (BetContext, int64, error) {
	bet := game.BetModel
	if override > 0 {
		return BetContext{
			LineCount:          bet.LineCount,
			CoinValueScale:     bet.CoinValueScale,
			DefaultCoinValue:   bet.DefaultCoinValue,
			TotalBetMinorUnits: override,
			BetModelType:       bet.Type,
		}, override, nil
	}
	if bet.TotalBetMinorUnits > 0 {
		return BetContext{
			LineCount:          bet.LineCount,
			CoinValueScale:     bet.CoinValueScale,
			DefaultCoinValue:   bet.DefaultCoinValue,
			TotalBetMinorUnits: int64(bet.TotalBetMinorUnits),
			BetModelType:       bet.Type,
		}, int64(bet.TotalBetMinorUnits), nil
	}
	lines := bet.LineCount
	if lines <= 0 {
		lines = 1
	}
	scale := bet.CoinValueScale
	if scale <= 0 {
		scale = 1
	}
	coin := bet.DefaultCoinValue
	if coin <= 0 {
		coin = 1
	}
	total := int64(lines * coin * scale)
	return BetContext{
		LineCount:          bet.LineCount,
		CoinValueScale:     bet.CoinValueScale,
		DefaultCoinValue:   bet.DefaultCoinValue,
		TotalBetMinorUnits: total,
		BetModelType:       bet.Type,
	}, total, nil
}

func resolveLimits(game *domain.GameVersion) EffectiveLimits {
	defaults := platformLimits()
	limits := defaults
	if game.Session.RuntimeLimits != nil {
		rl := game.Session.RuntimeLimits
		if rl.MaxStepsPerSpinChain > 0 {
			limits.MaxStepsPerSpinChain = rl.MaxStepsPerSpinChain
		}
		if rl.MaxFramesPerChain > 0 {
			limits.MaxFramesPerChain = rl.MaxFramesPerChain
		}
		if rl.MaxTransitionsPerStep > 0 {
			limits.MaxTransitionsPerStep = rl.MaxTransitionsPerStep
		}
		if rl.MaxRespinsPerFeature > 0 {
			limits.MaxRespinsPerFeature = rl.MaxRespinsPerFeature
		}
		if rl.MaxEventsPerChain > 0 {
			limits.MaxEventsPerChain = rl.MaxEventsPerChain
		}
		if rl.MaxWallClockMsPerChain > 0 {
			limits.MaxWallClockMsPerChain = rl.MaxWallClockMsPerChain
		}
	}
	maxStack := game.Session.MaxStackDepth
	if maxStack <= 0 {
		maxStack = 8
	}
	if limits.MaxFramesPerChain <= 0 || limits.MaxFramesPerChain > maxStack {
		limits.MaxFramesPerChain = maxStack
	}
	return limits
}

func platformLimits() EffectiveLimits {
	return EffectiveLimits{
		MaxStepsPerSpinChain:   500,
		MaxFramesPerChain:      8,
		MaxTransitionsPerStep:  8,
		MaxRespinsPerFeature:   100,
		MaxEventsPerChain:      10000,
		MaxWallClockMsPerChain: 0,
	}
}

func resolveExposure(game *domain.GameVersion, totalBet int64) ExposureState {
	exp := game.Exposure
	state := ExposureState{
		EnforceCap:       exp.EnforceCap,
		CapScope:         exp.CapScope,
		MaxWinMinorUnits: int64(exp.MaxWinMinorUnits),
		MaxWinMultiplier: int64(exp.MaxWinMultiplier),
	}
	cap := state.MaxWinMinorUnits
	if exp.MaxWinMultiplier > 0 && totalBet > 0 {
		multCap := int64(exp.MaxWinMultiplier) * totalBet
		if cap == 0 || multCap < cap {
			cap = multCap
		}
	}
	state.EffectiveCapMinor = cap
	return state
}
