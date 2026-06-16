package rng

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/binary"
	"fmt"
)

type Algorithm string

const AlgorithmPCG64 Algorithm = "PCG64"

type DerivationPolicy string

const PolicyV1HashShard DerivationPolicy = "v1-hash-shard"

type Config struct {
	Algorithm Algorithm
	Policy    DerivationPolicy
}

type Service struct {
	algorithm Algorithm
	policy    DerivationPolicy
}

func NewService(cfg Config) (*Service, error) {
	if cfg.Algorithm == "" {
		cfg.Algorithm = AlgorithmPCG64
	}
	if cfg.Policy == "" {
		cfg.Policy = PolicyV1HashShard
	}
	if cfg.Algorithm != AlgorithmPCG64 {
		return nil, fmt.Errorf("unsupported rng algorithm %q", cfg.Algorithm)
	}
	if cfg.Policy != PolicyV1HashShard {
		return nil, fmt.Errorf("unsupported seed derivation policy %q", cfg.Policy)
	}
	return &Service{algorithm: cfg.Algorithm, policy: cfg.Policy}, nil
}

type ChainScope struct {
	chainSeed []byte
}

func (s *Service) NewChainScope(masterSeed []byte, shardIndex int, simulationRunID string, spinChainIndex int64) *ChainScope {
	shardSeed := deriveSeed(masterSeed, encodeInt(shardIndex), []byte(simulationRunID))
	chainSeed := deriveSeed(shardSeed, encodeInt64(spinChainIndex))
	return &ChainScope{chainSeed: chainSeed}
}

func (c *ChainScope) ChainSeed() []byte {
	out := make([]byte, len(c.chainSeed))
	copy(out, c.chainSeed)
	return out
}

type FrameStream struct {
	frameStreamSeed []byte
}

func (c *ChainScope) FrameStream(frameID string) *FrameStream {
	seed := deriveSeed(c.chainSeed, []byte(frameID))
	return &FrameStream{frameStreamSeed: seed}
}

func (f *FrameStream) StepRNG(stepIndex int) *RNG {
	label := append([]byte("step:"), encodeInt(stepIndex)...)
	seed := deriveSeed(f.frameStreamSeed, label)
	return newRNG(seed)
}

func (f *FrameStream) MultiplierRNG(multiplierRefID string, applyIndex int) *RNG {
	label := append([]byte("mult:"), []byte(multiplierRefID)...)
	label = append(label, ':')
	label = append(label, encodeInt(applyIndex)...)
	seed := deriveSeed(f.frameStreamSeed, label)
	return newRNG(seed)
}

func deriveSeed(key []byte, parts ...[]byte) []byte {
	mac := hmac.New(sha256.New, key)
	for _, part := range parts {
		mac.Write(part)
	}
	sum := mac.Sum(nil)
	return sum
}

func encodeInt(v int) []byte {
	buf := make([]byte, 8)
	binary.BigEndian.PutUint64(buf, uint64(v))
	return buf
}

func encodeInt64(v int64) []byte {
	buf := make([]byte, 8)
	binary.BigEndian.PutUint64(buf, uint64(v))
	return buf
}

func seedToPCG64State(seed []byte) (state, seq uint64) {
	if len(seed) < 16 {
		padded := make([]byte, 16)
		copy(padded, seed)
		seed = padded
	}
	state = binary.BigEndian.Uint64(seed[:8])
	seq = binary.BigEndian.Uint64(seed[8:16])
	if seq == 0 {
		seq = 54
	}
	return state, seq
}

func newRNG(seed []byte) *RNG {
	state, seq := seedToPCG64State(seed)
	return &RNG{pcg: newPCG64(state, seq)}
}

// RNG implements the plugin-facing draw interface.
type RNG struct {
	pcg    *PCG64
	drawID int
}

func (r *RNG) NextUint64() uint64 {
	r.drawID++
	return r.pcg.NextUint64()
}

func (r *RNG) NextInt(n int) int {
	if n <= 0 {
		panic(fmt.Sprintf("rng: NextInt requires n > 0, got %d", n))
	}
	if n == 1 {
		r.drawID++
		return 0
	}
	max := uint64(n)
	limit := (^uint64(0) / max) * max
	for {
		x := r.pcg.NextUint64()
		if x < limit {
			r.drawID++
			return int(x % max)
		}
	}
}

func (r *RNG) DrawID() int {
	return r.drawID
}
