package runtime

import "math-assistant/runtime-core/internal/domain"

// EventLogMode controls which runtime events are recorded (Simulation Profile §12.5).
type EventLogMode string

const (
	EventLogModeNone            EventLogMode = "none"
	EventLogModeTransitionsOnly EventLogMode = "transitions_only"
	EventLogModeFull            EventLogMode = "full"
	EventLogModeReplay          EventLogMode = "replay"
)

// SpinChainRequest is input for one simulated spin chain (Runtime Core §6.3).
type SpinChainRequest struct {
	Game             *domain.GameVersion
	Profile          *SimulationProfile
	MasterSeed       []byte
	SpinChainIndex   int64
	BetMinorUnits    int64
	ShardIndex       int
	SimulationRunID  string
	EngineVersion    string
	EventLogMode     EventLogMode
}

// SimulationProfile holds non-canonical simulation parameters (subset for R1).
type SimulationProfile struct {
	ProfileVersion         string
	GameVersionContentHash string
}

// SpinChainResult is output from one spin chain execution (Runtime Core §6.3).
type SpinChainResult struct {
	TotalWinMinorUnits         int64
	TotalUncappedWinMinorUnits int64
	TotalTruncatedMinorUnits   int64
	TotalBetMinorUnits         int64
	StepCount                  int
	FramePushCount             int
	ExposureCapApplied         bool
	LimitHit                   *LimitHit
	Fault                      *ChainFault
	Events                     []Event
	EventLogHash               string
	AccumulatorDelta           AccumulatorDelta
}

// LimitHit records a runtime safety limit breach (Canonical §18).
type LimitHit struct {
	Code   string
	Action string
}

// ChainFault records an abnormal chain termination (Runtime Core §20).
type ChainFault struct {
	Code        string
	Message     string
	FrameID     string
	PluginRefID string
}

// AccumulatorDelta holds commutative counters for the Mathematical Engine.
type AccumulatorDelta struct {
	CappedWinMinorUnits        int64
	UncappedWinMinorUnits      int64
	ExposureTruncationCount    int64
	ExposureTruncatedMinorUnits int64
	ChainFaultCount            int64
}
