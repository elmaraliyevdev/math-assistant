package runtime

import (
	"fmt"

	"math-assistant/runtime-core/internal/domain"
	isession "math-assistant/runtime-core/internal/runtime/session"
)

// BetContext is immutable bet information for a spin chain (Runtime Core §14.3).
type BetContext struct {
	LineCount          int
	CoinValueScale     int
	DefaultCoinValue   int
	TotalBetMinorUnits int64
	BetModelType       string
}

// EffectiveLimits are resolved runtime safety limits for a chain (Canonical §18).
type EffectiveLimits struct {
	MaxStepsPerSpinChain   int
	MaxFramesPerChain      int
	MaxTransitionsPerStep  int
	MaxRespinsPerFeature   int
	MaxEventsPerChain      int
	MaxWallClockMsPerChain int
}

// ExposureState holds runtime exposure cap enforcement state (Runtime Core §16).
type ExposureState struct {
	EnforceCap         bool
	EffectiveCapMinor  int64
	CapScope           string
	MaxWinMinorUnits   int64
	MaxWinMultiplier   int64
}

// SessionContext is mutable per-chain runtime state (Runtime Core §7.1).
type SessionContext struct {
	GameVersionContentHash     string
	EngineVersion              string
	SpinChainIndex             int64
	Bet                        BetContext
	TotalBetMinorUnits           int64
	TotalWinMinorUnits           int64
	TotalUncappedWinMinorUnits   int64
	TotalTruncatedMinorUnits     int64
	ExposureCapApplied           bool
	InheritancePolicy            string
	RNG                          *RNGService
	ChainRNG                     ChainScope
	Events                       *EventLogger
	Limits                       EffectiveLimits
	Exposure                     ExposureState
}

// NewSessionParams configures SessionContext construction for phase R1.
type NewSessionParams struct {
	Game            *domain.GameVersion
	EngineVersion   string
	MasterSeed      []byte
	SpinChainIndex  int64
	ShardIndex      int
	SimulationRunID string
	BetMinorUnits   int64
	EventLogMode    EventLogMode
	RNGConfig       RNGServiceConfig
}

// NewSessionParamsFromRequest maps a SpinChainRequest to session construction params.
func NewSessionParamsFromRequest(req SpinChainRequest) NewSessionParams {
	engineVersion := req.EngineVersion
	if engineVersion == "" {
		engineVersion = EngineVersion
	}
	rngCfg := DefaultRNGServiceConfig()
	return NewSessionParams{
		Game:            req.Game,
		EngineVersion:   engineVersion,
		MasterSeed:      req.MasterSeed,
		SpinChainIndex:  req.SpinChainIndex,
		ShardIndex:      req.ShardIndex,
		SimulationRunID: req.SimulationRunID,
		BetMinorUnits:   req.BetMinorUnits,
		EventLogMode:    req.EventLogMode,
		RNGConfig:       rngCfg,
	}
}

// NewSessionContext constructs a session for one spin chain.
func NewSessionContext(params NewSessionParams) (*SessionContext, error) {
	inner, err := isession.New(isession.Params{
		Game:            params.Game,
		EngineVersion:   params.EngineVersion,
		MasterSeed:      params.MasterSeed,
		SpinChainIndex:  params.SpinChainIndex,
		ShardIndex:      params.ShardIndex,
		SimulationRunID: params.SimulationRunID,
		BetMinorUnits:   params.BetMinorUnits,
		EventLogMode:    isession.EventLogMode(params.EventLogMode),
		RNGConfig: isession.RNGConfig{
			Algorithm: isession.RNGAlgorithm(params.RNGConfig.Algorithm),
			Policy:    isession.RNGPolicy(params.RNGConfig.Policy),
		},
	})
	if err != nil {
		return nil, err
	}
	rngSvc, err := NewRNGService(params.RNGConfig)
	if err != nil {
		return nil, fmt.Errorf("rng service: %w", err)
	}
	chainScope := rngSvc.NewChainScope(params.MasterSeed, params.ShardIndex, params.SimulationRunID, params.SpinChainIndex)
	logger := NewEventLogger(params.EventLogMode, EventCorrelation{
		SimulationRunID:        params.SimulationRunID,
		SpinChainIndex:         params.SpinChainIndex,
		GameVersionContentHash: inner.GameVersionContentHash,
		EngineVersion:          params.EngineVersion,
	})
	return &SessionContext{
		GameVersionContentHash:   inner.GameVersionContentHash,
		EngineVersion:            inner.EngineVersion,
		SpinChainIndex:           inner.SpinChainIndex,
		Bet:                      mapBetContext(inner.Bet),
		TotalBetMinorUnits:       inner.TotalBetMinorUnits,
		InheritancePolicy:        inner.InheritancePolicy,
		RNG:                      rngSvc,
		ChainRNG:                 chainScope,
		Events:                   logger,
		Limits:                   mapLimits(inner.Limits),
		Exposure:                 mapExposure(inner.Exposure),
	}, nil
}

func mapBetContext(b isession.BetContext) BetContext {
	return BetContext{
		LineCount:          b.LineCount,
		CoinValueScale:     b.CoinValueScale,
		DefaultCoinValue:   b.DefaultCoinValue,
		TotalBetMinorUnits: b.TotalBetMinorUnits,
		BetModelType:       b.BetModelType,
	}
}

func mapLimits(l isession.EffectiveLimits) EffectiveLimits {
	return EffectiveLimits{
		MaxStepsPerSpinChain:   l.MaxStepsPerSpinChain,
		MaxFramesPerChain:      l.MaxFramesPerChain,
		MaxTransitionsPerStep:  l.MaxTransitionsPerStep,
		MaxRespinsPerFeature:   l.MaxRespinsPerFeature,
		MaxEventsPerChain:      l.MaxEventsPerChain,
		MaxWallClockMsPerChain: l.MaxWallClockMsPerChain,
	}
}

func mapExposure(e isession.ExposureState) ExposureState {
	return ExposureState{
		EnforceCap:        e.EnforceCap,
		EffectiveCapMinor: e.EffectiveCapMinor,
		CapScope:          e.CapScope,
		MaxWinMinorUnits:  e.MaxWinMinorUnits,
		MaxWinMultiplier:  e.MaxWinMultiplier,
	}
}
