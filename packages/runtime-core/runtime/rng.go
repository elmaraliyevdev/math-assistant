package runtime

import irng "math-assistant/runtime-core/internal/runtime/rng"

// RNG is the plugin-facing random number interface (Runtime Core §13.4).
type RNG interface {
	NextUint64() uint64
	NextInt(n int) int
	DrawID() int
}

// SeedDerivationPolicy identifies the HMAC seed derivation scheme.
type SeedDerivationPolicy string

const (
	SeedDerivationV1HashShard SeedDerivationPolicy = "v1-hash-shard"
)

// RNGAlgorithm identifies the PRNG algorithm family.
type RNGAlgorithm string

const (
	RNGAlgorithmPCG64 RNGAlgorithm = "PCG64"
)

// RNGServiceConfig configures deterministic RNG derivation.
type RNGServiceConfig struct {
	Algorithm RNGAlgorithm
	Policy    SeedDerivationPolicy
}

// DefaultRNGServiceConfig returns MVP defaults from Canonical Appendix A.
func DefaultRNGServiceConfig() RNGServiceConfig {
	return RNGServiceConfig{
		Algorithm: RNGAlgorithmPCG64,
		Policy:    SeedDerivationV1HashShard,
	}
}

// RNGService derives scoped deterministic RNG streams for spin chains.
type RNGService struct {
	inner *irng.Service
}

// NewRNGService constructs an RNG service.
func NewRNGService(cfg RNGServiceConfig) (*RNGService, error) {
	s, err := irng.NewService(irng.Config{
		Algorithm: irng.Algorithm(cfg.Algorithm),
		Policy:    irng.DerivationPolicy(cfg.Policy),
	})
	if err != nil {
		return nil, err
	}
	return &RNGService{inner: s}, nil
}

// ChainScope holds derived seeds for one spin chain.
type ChainScope struct {
	inner *irng.ChainScope
}

// NewChainScope derives shard and chain seeds per Runtime Core §13.3.
func (s *RNGService) NewChainScope(masterSeed []byte, shardIndex int, simulationRunID string, spinChainIndex int64) ChainScope {
	return ChainScope{inner: s.inner.NewChainScope(masterSeed, shardIndex, simulationRunID, spinChainIndex)}
}

// ChainSeed returns the derived chain seed bytes (for diagnostics and tests).
func (c ChainScope) ChainSeed() []byte {
	return c.inner.ChainSeed()
}

// FrameStream returns a persistent frame-level stream allocator.
func (c ChainScope) FrameStream(frameID string) *FrameStream {
	return &FrameStream{inner: c.inner.FrameStream(frameID)}
}

// FrameStream mints step and multiplier RNG streams for one stack frame.
type FrameStream struct {
	inner *irng.FrameStream
}

// StepRNG returns an RNG for one ExecuteStep (fresh derivation per step index).
func (f *FrameStream) StepRNG(stepIndex int) RNG {
	return f.inner.StepRNG(stepIndex)
}

// MultiplierRNG returns an independent RNG for one multiplier application.
func (f *FrameStream) MultiplierRNG(multiplierRefID string, applyIndex int) RNG {
	return f.inner.MultiplierRNG(multiplierRefID, applyIndex)
}
