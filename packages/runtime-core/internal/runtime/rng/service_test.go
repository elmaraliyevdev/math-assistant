package rng

import (
	"bytes"
	"testing"
)

func TestNewServiceDefaults(t *testing.T) {
	s, err := NewService(Config{})
	if err != nil {
		t.Fatalf("NewService: %v", err)
	}
	if s.algorithm != AlgorithmPCG64 || s.policy != PolicyV1HashShard {
		t.Fatalf("unexpected defaults: %+v", s)
	}
}

func TestNewServiceInvalidConfig(t *testing.T) {
	if _, err := NewService(Config{Algorithm: "LCG"}); err == nil {
		t.Fatal("expected error for unsupported algorithm")
	}
	if _, err := NewService(Config{Policy: "legacy"}); err == nil {
		t.Fatal("expected error for unsupported policy")
	}
}

func TestChainSeedDerivationStable(t *testing.T) {
	s, err := NewService(Config{})
	if err != nil {
		t.Fatal(err)
	}
	master := []byte("master-seed-bytes")
	runID := "run-abc"
	scopeA := s.NewChainScope(master, 0, runID, 42)
	scopeB := s.NewChainScope(master, 0, runID, 42)
	if !bytes.Equal(scopeA.ChainSeed(), scopeB.ChainSeed()) {
		t.Fatal("chain seed must be deterministic for identical inputs")
	}
}

func TestChainSeedDerivationDistinct(t *testing.T) {
	s, _ := NewService(Config{})
	master := []byte("master-seed-bytes")
	base := s.NewChainScope(master, 0, "run", 1).ChainSeed()
	shard := s.NewChainScope(master, 1, "run", 1).ChainSeed()
	chain := s.NewChainScope(master, 0, "run", 2).ChainSeed()
	run := s.NewChainScope(master, 0, "run-other", 1).ChainSeed()
	for name, got := range map[string][]byte{
		"shard": shard, "chain": chain, "run": run,
	} {
		if bytes.Equal(base, got) {
			t.Fatalf("%s seed should differ from base", name)
		}
	}
}

func TestStepAndMultiplierStreamsIndependent(t *testing.T) {
	s, _ := NewService(Config{})
	scope := s.NewChainScope([]byte("seed"), 0, "run", 0)
	frame := scope.FrameStream("f-0-0")

	step0 := frame.StepRNG(0)
	step1 := frame.StepRNG(1)
	if step0.NextUint64() == step1.NextUint64() {
		t.Fatal("step streams must be independent")
	}

	multA := frame.MultiplierRNG("mult.ref", 0)
	multB := frame.MultiplierRNG("mult.ref", 1)
	if multA.NextUint64() == multB.NextUint64() {
		t.Fatal("multiplier streams must be independent")
	}
	if multA.NextUint64() == step0.NextUint64() {
		t.Fatal("multiplier and step streams must differ")
	}
}

func TestRNGNextIntBounds(t *testing.T) {
	s, _ := NewService(Config{})
	rng := s.NewChainScope([]byte("int-bounds"), 0, "run", 0).
		FrameStream("frame").StepRNG(0)
	const n = 17
	const draws = 5000
	for i := 0; i < draws; i++ {
		v := rng.NextInt(n)
		if v < 0 || v >= n {
			t.Fatalf("NextInt(%d) = %d out of range", n, v)
		}
	}
}

func TestRNGNextIntOne(t *testing.T) {
	rng := newRNG([]byte("one"))
	if got := rng.NextInt(1); got != 0 {
		t.Fatalf("NextInt(1) = %d, want 0", got)
	}
	if rng.DrawID() != 1 {
		t.Fatalf("DrawID = %d, want 1", rng.DrawID())
	}
}

func TestRNGNextIntPanicsOnInvalidN(t *testing.T) {
	rng := newRNG([]byte("panic"))
	defer func() {
		if recover() == nil {
			t.Fatal("expected panic for n <= 0")
		}
	}()
	rng.NextInt(0)
}

func TestRNGDrawIDIncrements(t *testing.T) {
	rng := newRNG([]byte("draw-id"))
	if rng.DrawID() != 0 {
		t.Fatalf("initial DrawID = %d", rng.DrawID())
	}
	rng.NextUint64()
	rng.NextInt(5)
	if rng.DrawID() != 2 {
		t.Fatalf("DrawID = %d, want 2", rng.DrawID())
	}
}

func TestSeedToPCG64StatePadsShortSeed(t *testing.T) {
	state, seq := seedToPCG64State([]byte{1, 2, 3})
	if state == 0 && seq == 0 {
		t.Fatal("expected non-zero state/seq from padded seed")
	}
}

func TestSeedToPCG64StateZeroSeqUsesDefault(t *testing.T) {
	seed := make([]byte, 16)
	_, seq := seedToPCG64State(seed)
	if seq != 54 {
		t.Fatalf("seq = %d, want default 54 when encoded seq is zero", seq)
	}
}

func TestChainSeedCopyIsolated(t *testing.T) {
	s, _ := NewService(Config{})
	scope := s.NewChainScope([]byte("copy"), 0, "run", 0)
	seed := scope.ChainSeed()
	seed[0] ^= 0xff
	if bytes.Equal(seed, scope.ChainSeed()) {
		t.Fatal("ChainSeed copy must not mutate internal seed")
	}
}
