package domain

// GameVersion is the canonical game mathematics document (schema v1.0.0).
type GameVersion struct {
	SchemaVersion         string                     `json:"schemaVersion"`
	GameVersion           GameVersionMeta            `json:"gameVersion"`
	Metadata              Metadata                   `json:"metadata"`
	GameConfig            GameConfig                 `json:"gameConfig"`
	Symbols               map[string]Symbol          `json:"symbols"`
	ReelSets              map[string]ReelSet         `json:"reelSets"`
	Paytable              Paytable                   `json:"paytable"`
	WinModel              WinModel                   `json:"winModel"`
	BetModel              BetModel                   `json:"betModel"`
	Plugins               map[string]PluginRef       `json:"plugins"`
	StateMachines         map[string]StateMachine    `json:"stateMachines"`
	Session               SessionConfig              `json:"session"`
	Exposure              Exposure                   `json:"exposure"`
	Determinism           Determinism                `json:"determinism"`
	Precedence            Precedence                 `json:"precedence"`
	Extensions            map[string]any             `json:"extensions"`
	RtpCategoryRegistry   *RtpCategoryRegistry       `json:"rtpCategoryRegistry,omitempty"`
	ValidationMetadata    *ValidationMetadataDoc     `json:"validationMetadata,omitempty"`
	ContentHash           string                     `json:"contentHash,omitempty"`
}

type GameVersionMeta struct {
	ID            string  `json:"id"`
	ProjectID     string  `json:"projectId"`
	VersionNumber int     `json:"versionNumber"`
	Status        string  `json:"status"`
	CreatedAt     string  `json:"createdAt"`
	PublishedAt   *string `json:"publishedAt,omitempty"`
	CreatedBy     string  `json:"createdBy,omitempty"`
	Label         string  `json:"label,omitempty"`
	Source        string  `json:"source,omitempty"`
}

type Metadata struct {
	Title            string     `json:"title"`
	Description      string     `json:"description,omitempty"`
	Tags             []string   `json:"tags,omitempty"`
	RtpTarget        *RtpTarget `json:"rtpTarget,omitempty"`
	VolatilityTarget string     `json:"volatilityTarget,omitempty"`
}

type RtpTarget struct {
	Percent   float64 `json:"percent"`
	Tolerance float64 `json:"tolerance,omitempty"`
}

type GameConfig struct {
	Grid             GridSpec `json:"grid"`
	DefaultReelSetID string   `json:"defaultReelSetId"`
}

type GridSpec struct {
	Reels       int    `json:"reels"`
	Rows        int    `json:"rows"`
	IndexOrigin string `json:"indexOrigin,omitempty"`
}

type Symbol struct {
	ID           string         `json:"id"`
	DisplayName  string         `json:"displayName,omitempty"`
	Type         string         `json:"type"`
	Pays         *bool          `json:"pays,omitempty"`
	Substitutes  []string       `json:"substitutes,omitempty"`
	Properties   map[string]any `json:"properties,omitempty"`
}

type ReelSet struct {
	ID    string      `json:"id"`
	Reels []ReelStrip `json:"reels"`
}

type ReelStrip struct {
	ReelIndex int      `json:"reelIndex"`
	Symbols   []string `json:"symbols"`
	Weights   []int    `json:"weights,omitempty"`
}

type Paytable struct {
	Lines []PaylineDefinition `json:"lines,omitempty"`
	Pays  []PaytableEntry     `json:"pays"`
}

type PaylineDefinition struct {
	Index int   `json:"index"`
	Path  []int `json:"path"`
}

type PaytableEntry struct {
	SymbolID   string `json:"symbolId"`
	Count      int    `json:"count"`
	Multiplier any    `json:"multiplier"`
}

type WinModel struct {
	Type                  string `json:"type"`
	Direction             string `json:"direction,omitempty"`
	ScatterPaysOnReels    *bool  `json:"scatterPaysOnReels,omitempty"`
	HighestWinOnlyPerLine *bool  `json:"highestWinOnlyPerLine,omitempty"`
}

type BetModel struct {
	Type               string `json:"type"`
	LineCount          int    `json:"lineCount,omitempty"`
	CoinValueScale     int    `json:"coinValueScale"`
	DefaultCoinValue   int    `json:"defaultCoinValue"`
	MinCoinValue       int    `json:"minCoinValue"`
	MaxCoinValue       int    `json:"maxCoinValue"`
	TotalBetMinorUnits int    `json:"totalBetMinorUnits,omitempty"`
}

type PluginRef struct {
	RefID               string   `json:"refId"`
	PluginID            string   `json:"pluginId"`
	PluginVersion       string   `json:"pluginVersion"`
	ConfigSchemaVersion string   `json:"configSchemaVersion"`
	Capabilities        []string `json:"capabilities"`
}

type StateMachine struct {
	ID             string           `json:"id"`
	Label          string           `json:"label,omitempty"`
	InitialStateID string           `json:"initialStateId"`
	States         map[string]State `json:"states"`
}

type State struct {
	ID           string         `json:"id"`
	Label        string         `json:"label,omitempty"`
	PluginRefID  string         `json:"pluginRefId"`
	StateType    string         `json:"stateType"`
	Terminal     bool           `json:"terminal"`
	RtpCategory  string         `json:"rtpCategory"`
	PluginConfig map[string]any `json:"pluginConfig"`
	Transitions  []Transition   `json:"transitions"`
	Progression  *Progression   `json:"progression,omitempty"`
	Deprecated   bool           `json:"deprecated,omitempty"`
}

type Progression struct {
	CounterField   string `json:"counterField,omitempty"`
	DecrementsOn   string `json:"decrementsOn,omitempty"`
	MinValue       *int   `json:"minValue,omitempty"`
	TerminatesWhen string `json:"terminatesWhen,omitempty"`
}

type Transition struct {
	ID               string         `json:"id"`
	Label            string         `json:"label,omitempty"`
	Trigger          string         `json:"trigger"`
	Priority         int            `json:"priority"`
	PriorityTier     string         `json:"priorityTier,omitempty"`
	Guard            map[string]any `json:"guard,omitempty"`
	Effect           string         `json:"effect"`
	TargetStateID    string         `json:"targetStateId,omitempty"`
	TargetMachineID  string         `json:"targetMachineId,omitempty"`
	Actions          []any          `json:"actions,omitempty"`
}

type SessionConfig struct {
	RootMachineID            string         `json:"rootMachineId"`
	RootStateID              string         `json:"rootStateId,omitempty"`
	MaxStackDepth            int            `json:"maxStackDepth"`
	SpinLoopMode             string         `json:"spinLoopMode"`
	PersistentStore          map[string]any `json:"persistentStore,omitempty"`
	ContextInheritancePolicy string         `json:"contextInheritancePolicy,omitempty"`
	RuntimeLimits            *RuntimeLimits `json:"runtimeLimits,omitempty"`
}

type RuntimeLimits struct {
	MaxStepsPerSpinChain   int `json:"maxStepsPerSpinChain,omitempty"`
	MaxFramesPerChain      int `json:"maxFramesPerChain,omitempty"`
	MaxTransitionsPerStep  int `json:"maxTransitionsPerStep,omitempty"`
	MaxRespinsPerFeature   int `json:"maxRespinsPerFeature,omitempty"`
	MaxEventsPerChain      int `json:"maxEventsPerChain,omitempty"`
	MaxWallClockMsPerChain int `json:"maxWallClockMsPerChain,omitempty"`
}

type Exposure struct {
	MaxWinMinorUnits   int                     `json:"maxWinMinorUnits"`
	MaxWinMultiplier   int                     `json:"maxWinMultiplier,omitempty"`
	CapScope           string                  `json:"capScope"`
	EnforceCap         bool                    `json:"enforceCap"`
	ValidationMode     string                  `json:"validationMode"`
	SimulationAssisted *ExposureSimAssisted    `json:"simulationAssisted,omitempty"`
	ManualAttestation  *ExposureManualAttest   `json:"manualAttestation,omitempty"`
}

type ExposureSimAssisted struct {
	MinSpinCount                        int     `json:"minSpinCount"`
	ConfidenceLevel                     float64 `json:"confidenceLevel"`
	MaxObservedMustReachPercentOfCap    float64 `json:"maxObservedMustReachPercentOfCap"`
}

type ExposureManualAttest struct {
	AttestedBy             string `json:"attestedBy"`
	AttestedAt             string `json:"attestedAt"`
	EffectiveCapMinorUnits int    `json:"effectiveCapMinorUnits"`
	Rationale              string `json:"rationale"`
	ReviewTicket           string `json:"reviewTicket,omitempty"`
}

type Determinism struct {
	RngAlgorithm          string `json:"rngAlgorithm"`
	RngAlgorithmVersion   string `json:"rngAlgorithmVersion"`
	SeedDerivationPolicy  string `json:"seedDerivationPolicy"`
	MoneyRepresentation   string `json:"moneyRepresentation"`
	MoneyScale            int    `json:"moneyScale"`
}

type Precedence struct {
	TriggerOrder []string `json:"triggerOrder"`
}

type RtpCategoryRegistry struct {
	Extends    string                        `json:"extends"`
	Categories map[string]RtpCategoryDef     `json:"categories"`
}

type RtpCategoryDef struct {
	Label              string  `json:"label"`
	Parent             *string `json:"parent"`
	DecompositionGroup string  `json:"decompositionGroup"`
	Description        string  `json:"description,omitempty"`
}

type ValidationMetadataDoc struct {
	ValidatedAt      string `json:"validatedAt"`
	ValidatorVersion string `json:"validatorVersion"`
	ReportID         string `json:"reportId,omitempty"`
	ChecksPassed     []string `json:"checksPassed"`
	Warnings         []any    `json:"warnings,omitempty"`
}
