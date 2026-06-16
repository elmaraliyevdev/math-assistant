package runtime

// HeldSymbol records a symbol held on the grid for hold-and-win features (Runtime Core §15.3).
type HeldSymbol struct {
	Reel     int
	Row      int
	SymbolID string
}

// FrameContext is mutable per-stack-frame state (Runtime Core §6.2, §15.3).
// Populated by plugins in later phases; R1 defines the value object only.
type FrameContext struct {
	SpinsRemaining   int
	RespinsRemaining int
	HeldSymbols      []HeldSymbol
	ActiveMultiplier string
	FrameLocalState  map[string]any
}

// NewFrameContext returns an empty frame context for a newly pushed stack frame.
func NewFrameContext() FrameContext {
	return FrameContext{
		FrameLocalState: make(map[string]any),
	}
}
